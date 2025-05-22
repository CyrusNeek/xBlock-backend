from celery import shared_task
from django.utils import timezone
from subscription.models import UserSubscription, SubscriptionPlan
from subscription.services.user_subscription_service import UserSubscriptionService

@shared_task
def check_users_subscription():
    """Check all user subscriptions and assign free plan if expired."""
    now = timezone.now()
    
    expired_subscriptions = UserSubscription.objects.filter(
        status=UserSubscription.ACTIVE, end_date__lt=now
    )

    free_plan = SubscriptionPlan.objects.filter(pk=13).first() # free monthly

    if not free_plan:
        return "No base plan found."

    for subscription in expired_subscriptions:
        user = subscription.user
        subscription.status = UserSubscription.EXPIRED
        subscription.save(update_fields=["status"])

        user_subscription_service = UserSubscriptionService(user, subscription.brand_owner)
        user_subscription_service.create_user_subscription_from_plan(free_plan)
        

    return f"Checked {expired_subscriptions.count()} expired subscriptions."



