from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from web.tasks import task_user_assistant_creation
import logging
from report.tasks.periodic.update_assistant_vector_files import update_assistant_vector_files
from web.models import BrandOwner, User
from subscription.models import UserSubscription, SubscriptionPlan
from django.utils import timezone
from datetime import timedelta



logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def signal_user_creation(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Created user {instance.username}")
        task_user_assistant_creation.delay(instance.pk)
        return

    if instance.assistant_set.exists():
        update_assistant_vector_files.delay(instance.assistant_set.first().pk)


@receiver(pre_save, sender=User)
def reset_otp_fields(sender, instance, **kwargs):
    """
    Reset otp_expire_time and otp_attempts if otp_secret is updated.
    """
    if instance.pk:  
        try:
            old_instance = User.objects.get(pk=instance.pk)
        except User.DoesNotExist:
            return  

        if old_instance.otp_secret != instance.otp_secret:
            instance.otp_expire = timezone.now() + timedelta(minutes=5)
            
            instance.otp_attempts = 0


