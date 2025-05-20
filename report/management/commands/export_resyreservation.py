# your_app/management/commands/export_resyreservation.py

import csv
from django.core.management.base import BaseCommand
from report.models import ResyReservation


class Command(BaseCommand):
    help = 'Export ResyReservation data to CSV'

    def handle(self, *args, **kwargs):
        # Define the CSV file path
        file_path = 'resyreservation_data.csv'

        # Open the CSV file for writing
        with open(file_path, 'w', newline='') as csvfile:
            # Create a CSV writer
            csvwriter = csv.writer(csvfile)

            # Write the header row
            csvwriter.writerow([
                'ID',
                'Resy Auth',
                'Time',
                'Service',
                'Guest',
                'Phone',
                'Email',
                'Party Size',
                'Visit Note',
                'Reserve Number',
                'Reservation Date',
                'Table Number',
                'Status',
                'Created At'
            ])

            # Query all ResyReservation objects
            reservations = ResyReservation.objects.all()

            # Write data rows
            for reservation in reservations:
                csvwriter.writerow([
                    reservation.id,
                    reservation.resy_auth.pk,
                    reservation.time,
                    reservation.service,
                    reservation.guest,
                    reservation.phone,
                    reservation.email,
                    reservation.party_size,
                    reservation.visit_note,
                    reservation.reservation_date,
                    reservation.table,
                    reservation.status,
                    reservation.created_at
                ])

        self.stdout.write(self.style.SUCCESS(
            f'Successfully exported ResyReservation data to {file_path}'))
