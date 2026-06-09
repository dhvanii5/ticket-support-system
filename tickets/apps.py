from django.apps import AppConfig
import os


class TicketsConfig(AppConfig):
    name = "tickets"

    def ready(self):
        # Run background task only in the main process to prevent duplicate execution
        if os.environ.get('RUN_MAIN') == 'true':
            from .escalation import start_escalation_task
            start_escalation_task()
