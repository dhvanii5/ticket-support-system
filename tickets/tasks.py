from celery import shared_task
from django.utils import timezone
from tickets.models import Ticket
from audit.models import AuditLog

@shared_task
def escalate_stale_tickets():
    now = timezone.now()
    stale_tickets = Ticket.objects.filter(
        status='ASSIGNED',
        is_escalated=False,
        escalation_deadline__lt=now
    )
    count = 0
    for ticket in stale_tickets:
        ticket.is_escalated = True
        ticket.priority = 'URGENT'
        ticket.save()
        AuditLog.objects.create(
            ticket=ticket,
            performed_by=ticket.assigned_to,
            action='ESCALATED',
            note='Auto-escalated due to inactivity'
        )
        count += 1
    return f'{count} tickets escalated'