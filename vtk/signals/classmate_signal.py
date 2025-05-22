from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from web.utils import PushNotification
from vtk.tasks import task_xclassmate_diarization
from vtk.models import XClassmate
import logging

logger = logging.getLogger(__name__)


def signal_trigger_xclassmate_summarize(sender, instance, created, **kwargs):
    # if created:

    #     notif = PushNotification()
    #     notif.send_notification(
    #         user=instance.created_by,
    #         title=f"Voice to knowledge {instance.name}",
    #         body="Your new Voice to knowledge tasks have been created!",
    #     )
    pass


@receiver(pre_save, sender=XClassmate)
def trigger_xclassmate_diarization_if_url_updated(sender, instance, **kwargs):
    """
    Triggers the task_xclassmate_diarization task if the recording_file_url of  a XClassmate instance is updated from None to a non-null value.
    """

    if not instance.pk:
        return

    if (
        instance.recording_file_url
        and instance.uploaded
        and not instance.diarization_signal_triggered
    ):
        logger.info(f"Diarization task triggered for xclassmate: {instance.name}")
        task_xclassmate_diarization.delay(instance.pk)
