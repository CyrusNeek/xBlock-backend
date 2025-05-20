# a command to clear all Resy reservations

from django.core.management.base import BaseCommand

from report.models.report_user import ReportUser


class Command(BaseCommand):
    help = 'Clear all ReportUser'

    def handle(self, *args, **kwargs):
        # Query all ResyReservation objects
        reservations = ReportUser.objects.all()

        # Delete all ResyReservation objects
        reservations.delete()

        self.stdout.write(self.style.SUCCESS(
            'Successfully cleared all ReportUser'))
