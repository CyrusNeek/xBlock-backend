from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.timezone import now
from web.models import Task
from web.tasks import task_notify_user
from web.utils import PushNotification

@receiver(pre_save, sender=Task)
def signal_task_assignee_updated(sender, instance, **kwargs):
    """
    Signal triggered when assignee is updated:
        1. update assigned_date 
        2. trigger a notification
    """
    try:
        old_instance = Task.objects.get(pk=instance.pk)
        if (
            old_instance.assignee != instance.assignee
            and instance.assignee
        ):
            instance.assigned_date = now()
            message = f"You have been assigned a new task: {instance.description}"
            task_notify_user.delay(
                user_id=instance.assignee.id, 
                message=message,
            )
            notif = PushNotification()
            notif.send_notification(user=instance.assignee, title="New task assigned to you!", body=message)
    except Task.DoesNotExist:
        pass
