from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.conf import settings

from web.services.storage_service import StorageService
from report.models.ssh_key import SSHKey
from report.models import ToastAuth


import logging
import paramiko
import os

logger = logging.getLogger(__name__)


def generate_ssh_key(instance: ToastAuth):
    """
    Generates a ssh key to be used on getting the reports
    """
    base_path = settings.SSH_BASE_DIR
    os.makedirs(base_path, exist_ok=True)

    key = paramiko.RSAKey.generate(2048)

    private_key_location = base_path + str(instance.pk) + "_toast_private_key.pem"

    key.write_private_key_file(private_key_location)

    filename = "sshkeys/" + str(instance.pk) + "_toast_private_key.pem"

    StorageService().upload_file(private_key_location, filename)

    # S3Client.s3_client.upload_file(
    #     private_key_location, settings.AWS_STORAGE_BUCKET_NAME, filename
    # )

    public_key = key.get_base64()

    # logger.info("public_key", public_key)
    # logger.info("private_key_location", private_key_location)

    sshkey = SSHKey(
        public_key=public_key, private_key_location=filename, toast_auth=instance
    )

    return sshkey


# TODO: delete bucket file after instance deletion


# @receiver(pre_save, sender=ToastAuth)
# def signal_toast_auth_creation(sender, instance, created, **kwargs):
#     """
#     Triggered when a ToastAuth instance is created.
#     """
#     logger.info(f"New ToastAuth created with id {instance.id}. Triggering task to crawl history toast reports.")

#     task_crawl_history_toast_report.delay(instance.id)

# if created and instance.sshkey is None:
#     generate_ssh_key(instance)

# logger.info(f"ToastAuth with id {instance.id} updated. No action taken.")
