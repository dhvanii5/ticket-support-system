from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import AuditLog
from .serializers import AuditLogSerializer

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        ticket_id = self.request.query_params.get('ticket_id')
        qs = AuditLog.objects.select_related('ticket', 'performed_by')
        if ticket_id:
            qs = qs.filter(ticket_id=ticket_id)
        if user.role == 'USER':
            qs = qs.filter(ticket__created_by=user)
        elif user.role == 'AGENT':
            qs = qs.filter(ticket__assigned_to=user)
        return qs