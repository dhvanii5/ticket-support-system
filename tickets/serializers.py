from rest_framework import serializers
from .models import Ticket
from accounts.serializers import UserSerializer
from locations import services as location_services
from locations.services import LocationAPIError


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

    def validate(self, data):
        """Ensure the provided country/state/city exist according to the
        Location service. This enforces that clients cannot submit arbitrary
        free-text locations."""
        country = data.get('country')
        state = data.get('state')
        city = data.get('city')

        # Basic presence already validated by field validators above
        try:
            states = location_services.get_states(country)
        except LocationAPIError as exc:
            raise serializers.ValidationError({
                'country': f'Location service unavailable: {exc}'
            })

        state_names = {s['name'] for s in states}
        if state not in state_names:
            raise serializers.ValidationError({'state': 'State not found for country.'})

        try:
            cities = location_services.get_cities(state, country)
        except LocationAPIError as exc:
            raise serializers.ValidationError({
                'city': f'Location service unavailable: {exc}'
            })

        city_names = {c['name'] for c in cities}
        if city not in city_names:
            raise serializers.ValidationError({'city': 'City not found for state/country.'})

        return data

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
            # RESOLVED → CLOSED is supervisor-only (via the force_close action)
        }
        allowed = valid_transitions.get(ticket.status, [])
        if value not in allowed:
            raise serializers.ValidationError(
                f"Cannot transition from {ticket.status} to {value}. Allowed: {allowed}"
            )
        return value