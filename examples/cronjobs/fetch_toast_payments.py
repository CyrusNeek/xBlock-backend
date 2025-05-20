from report.models import ToastAuth
from report.tasks.periodic.toast.payment_details_crawl import (
    crawl_toast_payment_details,
)
from report.tasks.periodic.toast.crawler import ToastCrawler
from report.tasks.periodic.toast.order_details_crawl import after_last_cronjob


def main():
    toast = ToastAuth.objects.first()
    filename = "tmp-1.pem"

    dates = ToastCrawler(
        host=toast.host,
        username=toast.username,
        location_id=toast.location_id,
        private_key_path=filename,
        date_time=None,
        file_name="OrderDetails.csv",
    ).get_history()["list"]

    date_array = sorted(dates, key=int)

    after_last_cronjob(toast.pk, date_array),


if __name__ == "django.core.management.commands.shell":
    main()
