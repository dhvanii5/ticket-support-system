from rest_framework import serializers
from .models import Ticket
from accounts.serializers import UserSerializer


class TicketSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'is_escalated', 'created_by', 'assigned_to',
            'country', 'state', 'city',
            'created_at', 'updated_at', 'last_action_at'
        ]
        read_only_fields = ['status', 'is_escalated', 'created_by', 'last_action_at']


class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'title', 'description', 'priority', 'country', 'state', 'city']

    def validate_country(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Country is required.")
        return value.strip()

    def validate_state(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("State is required.")
        return value.strip()

    def validate_city(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("City is required.")
        return value.strip()

    def create(self, validated_data):
        from django.utils import timezone
        from datetime import timedelta
        ticket = Ticket.objects.create(
            **validated_data,
            created_by=self.context['request'].user,
            escalation_deadline=timezone.now() + timedelta(minutes=2)
        )
        return ticket


class TicketStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['status']

    def validate_status(self, value):
        ticket = self.instance
        valid_transitions = {
            'OPEN': ['ASSIGNED'],
            'ASSIGNED': ['IN_PROGRESS'],
            'IN_PROGRESS': ['RESOLVED'],
            'RESOLVED': ['CLOSED'],
        }
        allowed = valid_transitions.get(ticket.status, [])
        if value not in allowed:
            raise serializers.ValidationError(
                f"Cannot transition from {ticket.status} to {value}. Allowed: {allowed}"
            )
        return value