from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from web.models import ToastSalesSummaryReport, Unit, ToastAuth
from web.selenium import ToastSeleniumCrawler
import logging
import time

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fetches sales summary from Toast using Selenium crawler and saves to the database.'

    def add_arguments(self, parser):
        parser.add_argument('start_date', type=str, help='Start date (MM-DD-YYYY)')
        parser.add_argument('end_date', type=str, help='End date (MM-DD-YYYY)')
        parser.add_argument('unit_name', type=str, help='Name of the unit')

    def handle(self, *args, **options):
        start_date = datetime.strptime(options['start_date'], '%m/%d/%Y').date()  # Changed to %m/%d/%Y
        end_date = datetime.strptime(options['end_date'], '%m/%d/%Y').date()  # Changed to %m/%d/%Y
        unit_name = options['unit_name']

        # Create or get the specified unit
        unit, created = Unit.objects.get_or_create(name=unit_name)

        # Attempt to retrieve the corresponding ToastAuth
        try:
            toast_auth = ToastAuth.objects.get(unit=unit)
        except ToastAuth.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'No ToastAuth found for unit: {unit_name}'))
            return

        if not start_date or not end_date:
            self.stdout.write(self.style.ERROR('Invalid date format. Please use MM-DD-YYYY.'))
            return

        email = toast_auth.email
        password = toast_auth.password
        current_date = start_date
        
        while current_date <= end_date:
            try:
                # Initialize and run the crawler
                crawler = ToastSeleniumCrawler(email=email, password=password, date=current_date.strftime('%m/%d/%Y'))
                report_data = crawler.get_sales_summary_report()
                logger.info(f"Report {current_date}: {report_data}")
                
                # Update report and ToastAuth status upon successful crawling
                with transaction.atomic():
                    ToastSalesSummaryReport.objects.update_or_create(
                        unit=unit,
                        defaults={'report': report_data},
                    )
                    
                    # Update ToastAuth status to VERIFIED
                    toast_auth.status = ToastAuth.VERIFIED
                    toast_auth.save()

                self.stdout.write(self.style.SUCCESS(f'Successfully created/updated report for {current_date}'))

            except Exception as e:
                # Handle exceptions, possibly setting ToastAuth status to FAIL
                toast_auth.status = ToastAuth.FAIL
                toast_auth.save()
                self.stdout.write(self.style.ERROR(f'Failed to fetch report for {current_date}: {e}'))

            current_date += timedelta(days=1)
            time.sleep(2)
            