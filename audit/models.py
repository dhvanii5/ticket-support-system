from django.db import models
from django.conf import settings
from tickets.models import Ticket

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATED', 'Created'),
        ('ASSIGNED', 'Assigned'),
        ('ESCALATED', 'Escalated'),
        ('STATUS_CHANGED', 'Status Changed'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='logs')
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='audit_logs'
    )
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    note = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} on Ticket #{self.ticket.id}"