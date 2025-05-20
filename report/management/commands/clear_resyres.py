# a command to clear all Resy reservations

from django.core.management.base import BaseCommand

from report.models.resy_reservation import ResyReservation


class Command(BaseCommand):
    help = 'Clear all Resy reservations'

    def handle(self, *args, **kwargs):
        # Query all ResyReservation objects
        reservations = ResyReservation.objects.all()

        # Delete all ResyReservation objects
        reservations.delete()

        self.stdout.write(self.style.SUCCESS(
            'Successfully cleared all Resy reservations'))
