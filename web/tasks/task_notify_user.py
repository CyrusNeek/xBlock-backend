from django.conf import settings
from celery import shared_task
import logging
from web.models import User, Notification
logger = logging.getLogger(__name__)


@shared_task
def task_notify_user(user_id: int, message: str) -> None:
    """
    notify user by create a notification instance
    """
    user = User.objects.get(id=user_id)
    logger.info(f"Create notification for user {user_id}")
    Notification.objects.create(
        user=user,
        message=message,
    )

