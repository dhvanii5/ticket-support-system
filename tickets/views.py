from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import Ticket
from .serializers import TicketSerializer, TicketCreateSerializer, TicketStatusUpdateSerializer
from .permissions import IsUser, IsAgent, IsSupervisor, IsAgentOrSupervisor
from audit.models import AuditLog
from accounts.models import User

class TicketViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'USER':
            return Ticket.objects.filter(created_by=user).select_related(
                'created_by', 'assigned_to', 'country', 'state', 'city'
            )
        if user.role == 'AGENT':
            return Ticket.objects.filter(assigned_to=user).select_related(
                'created_by', 'assigned_to', 'country', 'state', 'city'
            )
        return Ticket.objects.all().select_related(
            'created_by', 'assigned_to', 'country', 'state', 'city'
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return TicketCreateSerializer
        if self.action == 'update_status':
            return TicketStatusUpdateSerializer
        return TicketSerializer

    def create(self, request, *args, **kwargs):
        if request.user.role != 'USER':
            return Response({'error': 'Only users can create tickets'}, status=403)
        serializer = TicketCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        ticket = serializer.save()
        AuditLog.objects.create(
            ticket=ticket, performed_by=request.user, action='CREATED'
        )
        return Response(TicketSerializer(ticket).data, status=201)

    @action(detail=True, methods=['post'], permission_classes=[IsSupervisor])
    def assign(self, request, pk=None):
        ticket = self.get_object()
        agent_id = request.data.get('agent_id')
        try:
            agent = User.objects.get(id=agent_id, role='AGENT')
        except User.DoesNotExist:
            return Response({'error': 'Agent not found'}, status=404)
        ticket.assigned_to = agent
        ticket.status = 'ASSIGNED'
        ticket.last_action_at = timezone.now()
        ticket.save()
        AuditLog.objects.create(
            ticket=ticket, performed_by=request.user,
            action='ASSIGNED', note=f'Assigned to {agent.username}'
        )
        return Response(TicketSerializer(ticket).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAgent])
    def update_status(self, request, pk=None):
        ticket = self.get_object()
        if ticket.assigned_to != request.user:
            return Response({'error': 'Not your ticket'}, status=403)
        serializer = TicketStatusUpdateSerializer(ticket, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data['status']
        serializer.save()
        ticket.last_action_at = timezone.now()
        ticket.save()
        action_map = {'IN_PROGRESS': 'STATUS_CHANGED', 'RESOLVED': 'RESOLVED'}
        AuditLog.objects.create(
            ticket=ticket, performed_by=request.user,
            action=action_map.get(new_status, 'STATUS_CHANGED'),
            note=f'Status changed to {new_status}'
        )
        return Response(TicketSerializer(ticket).data)

    @action(detail=True, methods=['post'], permission_classes=[IsSupervisor])
    def force_close(self, request, pk=None):
        ticket = self.get_object()
        ticket.status = 'CLOSED'
        ticket.save()
        AuditLog.objects.create(
            ticket=ticket, performed_by=request.user,
            action='CLOSED', note='Force closed by supervisor'
        )
        return Response(TicketSerializer(ticket).data)

    @action(detail=False, methods=['get'], permission_classes=[IsSupervisor])
    def escalated(self, request):
        tickets = Ticket.objects.filter(is_escalated=True).select_related(
            'created_by', 'assigned_to', 'country', 'state', 'city'
        )
        return Response(TicketSerializer(tickets, many=True).data)

    @action(detail=True, methods=['post'], permission_classes=[IsSupervisor])
    def reassign(self, request, pk=None):
        ticket = self.get_object()
        agent_id = request.data.get('agent_id')
        try:
            agent = User.objects.get(id=agent_id, role='AGENT')
        except User.DoesNotExist:
            return Response({'error': 'Agent not found'}, status=404)
        ticket.assigned_to = agent
        ticket.last_action_at = timezone.now()
        ticket.save()
        AuditLog.objects.create(
            ticket=ticket, performed_by=request.user,
            action='ASSIGNED', note=f'Reassigned to {agent.username}'
        )
        return Response(TicketSerializer(ticket).data)