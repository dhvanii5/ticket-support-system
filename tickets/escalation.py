import asyncio
import threading
import logging
from asgiref.sync import sync_to_async
from django.utils import timezone

logger = logging.getLogger(__name__)

@sync_to_async
def process_stale_tickets():
    # Import inside to ensure Django registry is fully populated
    from tickets.models import Ticket
    from audit.models import AuditLog
    
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
        
    if count > 0:
        logger.info(f"{count} tickets escalated")
    return count

async def escalation_loop():
    while True:
        try:
            await process_stale_tickets()
        except Exception as e:
            logger.error(f"Error in escalation task: {e}")
        
        # Run every 30 minutes
        await asyncio.sleep(30 * 60)

def start_escalation_task():
    def run_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(escalation_loop())

    thread = threading.Thread(target=run_loop, daemon=True, name="EscalationTaskThread")
    thread.start()
