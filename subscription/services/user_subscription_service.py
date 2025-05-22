from subscription.models import SubscriptionPlan, UserSubscription
from web.models import User, BrandOwner
from django.utils import timezone


class UserSubscriptionService:

    user : User 
    brand_owner : BrandOwner

    def __init__(self, user, brand_owner):
        self.user = user
        self.brand_owner = brand_owner
    

    def create_user_subscription_from_plan(self, plan : SubscriptionPlan):
        tokens_remaining, minutes_remaining, classmate_minutes_remaining = (
                    self.calculate_allocation(plan)
                )
        user_subscription = UserSubscription.objects.create(
                brand_owner=self.brand_owner,
                plan=plan,
                user=self.user,
                status=UserSubscription.ACTIVE,
                token_remaining=tokens_remaining,
                token_user_limit=plan.token_user_limit,
                total_tokens=tokens_remaining,
                # minute_remaining=minutes_remaining,
                meeting_user_limit=plan.meeting_user_limit,
                total_minutes=minutes_remaining,
                total_integration=plan.total_integration,
                upload_user_limit=plan.upload_user_limit,
                upload_size_remaining=plan.total_upload_allocation,
                total_upload_size=plan.total_upload_allocation,
                classmate_time_remaining=classmate_minutes_remaining,
                classmate_user_limit=plan.classmate_user_limit,
                total_classmate_minutes=classmate_minutes_remaining,
                last_allocation=timezone.now(),
                integration=plan.integration,
                max_sub_brand=plan.max_sub_brand,
                max_unit_per_brand=plan.max_unit_per_brand,
                start_date=timezone.now()
            )
        return user_subscription
        
    def calculate_allocation(self, subscription_plan):
        tokens_remaining = self.calculate_tokens(subscription_plan)
        minutes_remaining = self.calculate_minutes(subscription_plan)
        classmate_minutes_remaining = self.calculate_classmate_minutes(
            subscription_plan
        )

        return tokens_remaining, minutes_remaining, classmate_minutes_remaining
    
    def calculate_tokens(self, subscription_plan):
        if subscription_plan.token_usage_period == "daily":
            return (
                subscription_plan.total_token_allocation
                * subscription_plan.subscription_length_days
            )
        if subscription_plan.token_usage_period == "monthly":
            return subscription_plan.total_token_allocation * (
                subscription_plan.subscription_length_days // 30
            )
        return subscription_plan.total_token_allocation

    def calculate_minutes(self, subscription_plan):
        if subscription_plan.meeting_usage_period == "daily":
            return (
                subscription_plan.total_meeting_duration
                * subscription_plan.subscription_length_days
            )
        if subscription_plan.meeting_usage_period == "monthly":
            return subscription_plan.total_meeting_duration * (
                subscription_plan.subscription_length_days // 30
            )
        return subscription_plan.total_meeting_duration

    def calculate_classmate_minutes(self, subscription_plan):
        if subscription_plan.classmate_usage_period == "daily":
            return (
                subscription_plan.total_classmate_session_duration
                * subscription_plan.subscription_length_days
            )
        if subscription_plan.classmate_usage_period == "monthly":
            return subscription_plan.total_classmate_session_duration * (
                subscription_plan.subscription_length_days // 30
            )
        return subscription_plan.total_classmate_session_duration

    def calculate_upload_size(self, subscription_plan):
        if subscription_plan.upload_usage_period == "daily":
            return (
                subscription_plan.total_upload_allocation
                * subscription_plan.subscription_length_days
            )
        if subscription_plan.upload_usage_period == "monthly":
            return subscription_plan.total_upload_allocation * (
                subscription_plan.subscription_length_days // 30
            )
        return subscription_plan.upload_allocation