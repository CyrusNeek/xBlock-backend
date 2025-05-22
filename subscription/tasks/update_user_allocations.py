from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from subscription.models import UserSubscription, SubscriptionPlan
from web.models import BrandOwner, User
from roles.constants import (
    LIMITED_ANSWER_ACCESS,
    UNLIMITED_ANSWER_ACCESS,
    ACTIVE_MEETING_ACCESS,
    XCLASSMATE_ACCESS,
    UNLIMITED_CRUD_BLOCK_ACCESS,
)
import logging

logger = logging.getLogger(__name__)

# TODO allocate tokens and minutes

@shared_task
def allocate_brand_users_usages():
    subscriptions = UserSubscription.objects.all()
    current_time = timezone.now()
    
    for subscription in subscriptions:
        plan = SubscriptionPlan.objects.get(pk=subscription.plan.pk)
        brand = BrandOwner.objects.get(pk=subscription.brand_owner.pk)
        brand_users = User.objects.filter(affiliation=brand)
        
        # Check if allocation is due based on the periods
        token_allocate = False
        classmate_allocate = False
        meeting_allocate = False
        upload_allocate = False

        # Check token allocation period
        if plan.token_usage_period == 'daily':
            if current_time >= subscription.last_allocation + timedelta(days=1):
                token_allocate = True
        elif plan.token_usage_period == 'monthly':
            if current_time >= subscription.last_allocation + timedelta(days=30):
                token_allocate = True

        # Check meeting allocation period
        if plan.meeting_usage_period == 'daily':
            if current_time >= subscription.last_allocation + timedelta(days=1):
                meeting_allocate = True
        elif plan.meeting_usage_period == 'monthly':
            if current_time >= subscription.last_allocation + timedelta(days=30):
                meeting_allocate = True

        # Check classmate allocation period
        if plan.classmate_usage_period == 'daily':
            if current_time >= subscription.last_allocation + timedelta(days=1):
                classmate_allocate = True
        elif plan.classmate_usage_period == 'monthly':
            if current_time >= subscription.last_allocation + timedelta(days=30):
                classmate_allocate = True
                
        # Check upload allocation period
        if plan.upload_usage_period == 'daily':
            if current_time >= subscription.last_allocation + timedelta(days=1):
                upload_allocate = True
        elif plan.upload_usage_period == 'monthly':
            if current_time >= subscription.last_allocation + timedelta(days=30):
                upload_allocate = True

        xbrain_permissions = [
            LIMITED_ANSWER_ACCESS,
            UNLIMITED_ANSWER_ACCESS,
        ]

        classmate_permissions = [XCLASSMATE_ACCESS]
        meeting_permissions = [ACTIVE_MEETING_ACCESS]
        upload_permissions = [UNLIMITED_CRUD_BLOCK_ACCESS]

        meeting_limits = 0
        classmate_limits = 0
        token_limits = 0
        upload_limits = 0

        for user in brand_users:
            user_permissions = list(
                user.role.permissions.values_list("component_key", flat=True)
            )

            if any(permission in user_permissions for permission in xbrain_permissions) and token_allocate:
                if plan.token_user_limit >= token_limits:
                    user.tokens += plan.total_token_allocation
                    token_limits += 1

            if any(permission in user_permissions for permission in meeting_permissions) and meeting_allocate:
                if plan.meeting_user_limit >= meeting_limits:
                    user.minutes += plan.total_meeting_duration
                    meeting_limits += 1

            if any(permission in user_permissions for permission in classmate_permissions) and classmate_allocate:
                if plan.classmate_user_limit >= classmate_limits:
                    user.classmate_minutes += plan.total_classmate_session_duration
                    classmate_limits += 1
            
            if any(permission in user_permissions for permission in upload_permissions) and upload_allocate:
                if plan.upload_user_limit >= upload_limits:
                    user.upload_size += plan.total_upload_allocation
                    upload_limits += 1

            user.save(update_fields=["tokens", "xmeeting_minutes", "stk_minutes", "upload_size"])


        subscription.last_allocation = current_time
        subscription.save(update_fields=["last_allocation"])

        logger.info(f"User allocations updated successfully for subscription {subscription.pk}.")
