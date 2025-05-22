from datetime import datetime
from django.db import transaction
from django.shortcuts import get_object_or_404
from web.models import Notification, User
from subscription.models import UserSubscription, UserDailyUsage


def decrement_xmeeting_minutes(user_pk, duration):
    user = get_object_or_404(User, pk=user_pk)
    current_date = datetime.now().date()

    user_daily_xmeeting_used, _ = UserDailyUsage.objects.get_or_create(
        user=user, date=current_date
    )

    user_plan = UserSubscription.objects.filter(
        brand_owner=user.affiliation, status=UserSubscription.ACTIVE
    ).first()

    if not user_plan:
        Notification.objects.create(
            user=user,
            message="No active subscription found. Please subscribe to access meeting minutes.",
            title="Unable to find subscription plan",
        )
        return False

    if user.xmeeting_minutes > 0:
        remaining_daily_limit = max(
            user_plan.plan.daily_meeting_limit
            - user_daily_xmeeting_used.meetings_duration,
            0,
        )

        if remaining_daily_limit <= 0:
            Notification.objects.create(
                user=user,
                message="You've reached your daily meeting minutes limit. Please try again tomorrow or consider upgrading your plan.",
                title="Daily Meeting Minutes Limit Reached",
            )
            return False

        decrement_duration = min(duration, remaining_daily_limit)

        with transaction.atomic():
            user.xmeeting_minutes = max(user.xmeeting_minutes - decrement_duration, 0)
            user_daily_xmeeting_used.meetings_duration += decrement_duration
            user.save()
            user_daily_xmeeting_used.save()

        return True

    Notification.objects.create(
        user=user,
        message="You've reached your total meeting minutes limit. Please manage your meeting usage or upgrade your plan.",
        title="Total Meeting Minutes Limit Reached",
    )
    return False
