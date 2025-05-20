from django.core.management.base import BaseCommand, CommandError
from web.tasks.selenium.task_crawl_unit_toast_report import task_crawl_unit_toast_report
from datetime import datetime

class Command(BaseCommand):
    help = """
    Schedules a crawl task for a given unit_id and date with a delay
    
    example usage: docker compose exec web python manage.py command_crawl_toast 15 20240220
    """

    def add_arguments(self, parser):
        # Define expected arguments
        parser.add_argument('unit_id', type=int, help='The ID of the unit to crawl')
        parser.add_argument('date', type=str, help='The date to crawl in YYYYMMDD format')

    def handle(self, *args, **options):
        unit_id = options['unit_id']
        date = options['date']

        # Basic validation of date format
        try:
            datetime.strptime(date, "%Y%m%d")
        except ValueError:
            raise CommandError('Date must be in YYYYMMDD format')

        task_crawl_unit_toast_report.delay(unit_id=unit_id, date=date)

        self.stdout.write(self.style.SUCCESS(f'Successfully scheduled crawl task for unit {unit_id} on {date}'))