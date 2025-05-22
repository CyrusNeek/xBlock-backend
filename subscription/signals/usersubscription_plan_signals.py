from django.db.models.signals import post_save
from django.dispatch import receiver
from subscription.models import UserSubscription, SubscriptionPlan
from web.models import BrandOwner, User
import logging
from roles.constants import (
    LIMITED_ANSWER_ACCESS,
    UNLIMITED_ANSWER_ACCESS,
    ACTIVE_MEETING_ACCESS,
    XCLASSMATE_ACCESS,
    UNLIMITED_CRUD_BLOCK_ACCESS,
)


logger = logging.getLogger(__name__)


@receiver(post_save, sender=UserSubscription)
def allocate_brand_users_usages(sender, instance, created, **kwargs):
    if created:
        plan = SubscriptionPlan.objects.get(pk=instance.plan.pk)
        print(plan)
        brand = BrandOwner.objects.get(pk=instance.brand_owner.pk)
        brand_users = User.objects.filter(affiliation=brand, role__isnull=False)

        xbrain_permissions = [
            LIMITED_ANSWER_ACCESS,
            UNLIMITED_ANSWER_ACCESS,
        ]
        
        upload_permissions = [UNLIMITED_CRUD_BLOCK_ACCESS]

        classmate_permissions = [XCLASSMATE_ACCESS]

        meeting_permissions = [ACTIVE_MEETING_ACCESS]

        meeting_limits = 0
        classmate_limits = 0
        token_limits = 0
        upload_limits = 0

        for user in brand_users:
            user_permissions = list(
                user.role.permissions.values_list("component_key", flat=True)
            )

            if any(permission in user_permissions for permission in xbrain_permissions):
                if plan.token_user_limit >= token_limits:
                    user.tokens = plan.total_token_allocation
                    token_limits += 1

            if any(permission in user_permissions for permission in meeting_permissions):
                if plan.meeting_user_limit >= meeting_limits:
                    user.xmeeting_minutes = plan.total_meeting_duration
                    meeting_limits += 1

            if any(permission in user_permissions for permission in classmate_permissions):
                if plan.classmate_user_limit >= classmate_limits:
                    user.stk_minutes = plan.total_classmate_session_duration
                    classmate_limits += 1
                    
            if any(permission in user_permissions for permission in upload_permissions):
                if plan.upload_user_limit >= upload_limits:
                    user.upload_size = plan.total_upload_allocation
                    upload_limits += 1
                    
            user.save(update_fields=["tokens", "xmeeting_minutes", "stk_minutes", "upload_size"])

        logger.info("user allocations updated successfully")
