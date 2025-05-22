from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from web.utils import PushNotification
from web.tasks import task_meeting_diarization
from web.models import Meeting
import logging

logger = logging.getLogger(__name__)


# @receiver(post_save, sender=Meeting)
def signal_trigger_meeting_summarize(sender, instance, created, **kwargs):
    if created:


        notif = PushNotification()
        notif.send_notification(
            user=instance.created_by,
            title=f"Meeting {instance.name}",
            body="Your new meeting tasks have been created!",
        )


@receiver(pre_save, sender=Meeting)
def trigger_meeting_diarization_if_url_updated(sender, instance, **kwargs):
    """
    Triggers the task_meeting_diarization task if the recording_file_url of a Meeting instance is updated from None to a non-null value.
    """

    if not instance.pk:
        return

    # previous_meeting = Meeting.objects.get(pk=instance.pk)
    if (
        instance.recording_file_url
        and instance.uploaded
        and not instance.diarization_signal_triggered
    ):
        logger.info(f"Diarization task triggered for meeting: {instance.name}")
        task_meeting_diarization.delay(instance.pk)
