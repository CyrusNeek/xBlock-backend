# a command to export all ReportUser and save to csv file

import csv
from report.models.report_user import ReportUser
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Export ReportUser data to CSV'

    def handle(self, *args, **kwargs):
        # Define the CSV file path
        file_path = 'reportuser_data.csv'

        # Open the CSV file for writing
        with open(file_path, 'w', newline='') as csvfile:
            # Create a CSV writer
            csvwriter = csv.writer(csvfile)

            # Write the header row
            csvwriter.writerow([
                'ID', 'Email', 'Phone', 'First Name', 'Last Name', 'Brand',
                'Created At', 'Updated At'
            ])

            # Query all ReportUser objects
            users = ReportUser.objects.all()

            # Write data rows
            for user in users:
                csvwriter.writerow([
                    user.id,
                    user.email,
                    user.phone,
                    user.first_name,
                    user.last_name,
                    user.brand,
                ])

        self.stdout.write(self.style.SUCCESS(
            f'Successfully exported ReportUser data to {file_path}'))
