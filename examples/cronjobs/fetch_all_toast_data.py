from report.models import ToastAuth
from report.tasks.periodic.toast.order_details_crawl import crawl_toast_order_details


def main():
    toast = ToastAuth.objects.first()
    crawl_toast_order_details(toast.pk, False)


if __name__ == "django.core.management.commands.shell":
    main()
