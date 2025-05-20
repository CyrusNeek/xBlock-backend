from web.services.storage_service import StorageService
from report.models import ToastAuth


from django.conf import settings


def main():
    toast = ToastAuth.objects.first()

    filename = f"tmp-1.pem"

    StorageService().download_file(toast.sshkey.private_key_location, filename)


if __name__ == "django.core.management.commands.shell":
    main()
