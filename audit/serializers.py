from rest_framework import serializers
from .models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    performed_by = serializers.StringRelatedField()
    ticket_id = serializers.IntegerField(source='ticket.id', read_only=True)

    class Meta:
        model = AuditLog
        fields = ['id', 'ticket_id', 'performed_by', 'action', 'note', 'timestamp']