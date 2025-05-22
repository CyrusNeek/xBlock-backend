from report.models import ResyAuth
from report.tasks.periodic.resy_crawler import get_valid_reservation_dates_and_fetch


def main():
    resy = ResyAuth.objects.first()

    print(get_valid_reservation_dates_and_fetch.delay(resy.pk))


if __name__ == "django.core.management.commands.shell":
    main()
