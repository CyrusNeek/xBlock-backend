import time
import sys
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to pause execution until database is available"""

    help = 'Wait for database connection to be available'

    def add_arguments(self, parser):
        parser.add_argument(
            '--timeout',
            type=int,
            default=60,
            help='Maximum time to wait for database in seconds'
        )

    def handle(self, *args, **options):
        """Handle the command"""
        self.stdout.write('Waiting for database...')
        timeout = options['timeout']
        start_time = time.time()
        
        while True:
            try:
                # Try to connect to all databases defined in settings
                for conn in connections.all():
                    conn.ensure_connection()
                    conn.close()
                self.stdout.write(self.style.SUCCESS('Database available!'))
                return
            except OperationalError:
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    self.stdout.write(self.style.ERROR(
                        f'Database unavailable, timeout of {timeout} seconds exceeded.'))
                    sys.exit(1)
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)
