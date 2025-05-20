from datetime import datetime
from web.models import Notification, User
from subscription.models import UserSubscription, UserDailyUsage
from django.shortcuts import get_object_or_404


def decrement_user_tokens(user_pk, token):
    user = get_object_or_404(User, pk=user_pk)
    current_date = datetime.now().date()
    user_daily_token_used, created = UserDailyUsage.objects.get_or_create(
        user=user, date=current_date
    )
    user_plan = UserSubscription.objects.filter(
        brand_owner=user.affiliation, status=UserSubscription.ACTIVE
    ).first()
    
    if user_daily_token_used is None :
        return False

    if user_daily_token_used.tokens_used >= user_plan.plan.daily_token_limit:
        Notification.objects.create(
            user=user,
            message="You have exhausted your daily token allotment for xBrain features. To continue utilizing these capabilities today, please consider upgrading your plan.",
            title="Daily Token Limit Reached",
        )
        return False

    if user.tokens > 0:
        user.tokens -= token
        user_daily_token_used.tokens_used += token
        user.save()
        user_daily_token_used.save()
        return True

    Notification.objects.create(
        user=user,
        message="Your current plan has reached its token limit for xBrain features. To continue utilizing these capabilities, please consider upgrading your subscription.",
        title="Token Limit Reached",
    )
    return False
