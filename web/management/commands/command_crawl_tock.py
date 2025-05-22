from django.core.management.base import BaseCommand, CommandError
from datetime import datetime

from web.tasks.selenium import task_crawl_unit_tock_reservation

class Command(BaseCommand):
    help = """
    Schedules a Tock reservation crawl task for a given unit and start_date and end_date with a delay. Format: YYYY-MM-DD.
    
    Example usage:
    docker compose exec web python manage.py command_crawl_tock 15 2024-03-05 2024-03-06
    """

    def add_arguments(self, parser):
        # Define expected arguments
        parser.add_argument('unit_id', type=int, help='The ID of the unit to crawl')
        parser.add_argument('start_date', type=str, help='The start date in YYYY-MM-DD format')
        parser.add_argument('end_date', type=str, help='The end date in YYYY-MM-DD format')

    def handle(self, *args, **options):
        unit_id = options['unit_id']
        start_date = options['start_date']
        end_date = options['end_date']
        # Basic validation of date format
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise CommandError('Date must be in YYYYMMDD format')

        task_crawl_unit_tock_reservation.delay(unit_id=unit_id, start_date=start_date, end_date=end_date)

        self.stdout.write(self.style.SUCCESS(f'Successfully scheduled crawl Tock reservation task for unit {unit_id} on {start_date} to {end_date}'))