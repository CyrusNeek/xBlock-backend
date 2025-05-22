from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db.transaction import on_commit
from web.tasks.unit_file import task_unit_file_upload_openai
from web.models import UnitFile
import logging

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=UnitFile)
def signal_unit_file_creation(sender, instance, **kwargs):
    """
    Triggered when File uploaded field is changed from False to True
    """
    if instance.id is not None:
        # Retrieve the instance from the database before it was saved
        prev_instance = UnitFile.objects.get(pk=instance.pk)
        # Check if 'uploaded' was changed from False to True
        if not prev_instance.uploaded and instance.uploaded:
            logger.info(f"UnitFile upload status changed to True: {instance.file_name}")
            on_commit(lambda: task_unit_file_upload_openai.delay(instance.id))
