from django.core.management.base import BaseCommand
from web.tasks.periodic_tasks import task_update_assistant_instruction 

class Command(BaseCommand):
    help = "Sync OpenAI assistant instruction time"

    def handle(self, *args, **kwargs):
        task_update_assistant_instruction.delay()
