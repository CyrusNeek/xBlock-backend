from django.contrib import admin
from django import forms
from django.utils import timezone
from .models import SubscriptionPlan, UserSubscription, MembershipBonus, Invoice, SubscriptionEmail
import json
from django.utils.safestring import mark_safe

class SubscriptionPlanForm(forms.ModelForm):
    class Meta:
        model = SubscriptionPlan
        fields = "__all__"
        labels = {
            "total_classmate_session_duration": "Total speech to Knowledge duration",
            "classmate_usage_period": " Speech to Knowledge usage period",
            "classmate_user_limit": "Speech to Knowledge user limit",
            "stk_session_length": "Speech to Knowledge session length",
            "daily_stk_limit": "Daily speech to Knowledge limit",
        }


@admin.register(SubscriptionPlan)
class PlanAdmin(admin.ModelAdmin):
    form = SubscriptionPlanForm
    exclude = ["is_primary"]
    list_display = ["name", "status", "subscription_price"]

@admin.register(SubscriptionEmail)
class SubscriptionEmailAdmin(admin.ModelAdmin):
    list_display = ["id", "title","days", "send_time","sender_email"]


@admin.register(UserSubscription)
class UserPlanAdmin(admin.ModelAdmin):
    readonly_fields = [
        field.name
        for field in UserSubscription._meta.get_fields()
        if field.name not in ("brand_owner", "plan", "user" , "email_ids")
    ] + ["pretty_email_ids"]

    list_display = ["plan", "brand_owner"]

    def pretty_email_ids(self, obj):
        if obj.email_ids:
            try:
                data = json.loads(obj.email_ids) if isinstance(obj.email_ids, str) else obj.email_ids
                pretty = json.dumps(data, indent=2)
                return mark_safe(f'<pre>{pretty}</pre>')
            except Exception:
                return obj.email_ids
        return ""
    pretty_email_ids.short_description = "Sent Email IDs"

    def save_model(self, request, obj, form, change):
        if not change:
            plan = obj.plan
            tokens_remaining, minutes_remaining, classmate_minutes_remaining = (
                self.calculate_allocation(plan)
            )

            active_user_plans = UserSubscription.objects.filter(
                status=UserSubscription.ACTIVE, user=obj.user
            )
            for active_plan in active_user_plans:
                active_plan.status = UserSubscription.CANCELED
                active_plan.save(update_fields=["status"])

            obj.status = UserSubscription.ACTIVE
            obj.token_remaining = tokens_remaining
            obj.token_user_limit = plan.token_user_limit
            obj.total_tokens = tokens_remaining
            obj.minute_remaining = minutes_remaining
            obj.meeting_user_limit = plan.meeting_user_limit
            obj.total_minutes = minutes_remaining
            obj.total_integration = plan.total_integration
            obj.upload_user_limit = plan.upload_user_limit
            obj.upload_size_remaining = plan.total_upload_allocation
            obj.total_upload_size = plan.total_upload_allocation
            obj.classmate_time_remaining = classmate_minutes_remaining
            obj.classmate_user_limit = plan.classmate_user_limit
            obj.total_classmate_minutes = classmate_minutes_remaining
            obj.last_allocation = timezone.now()
            obj.integration = plan.integration
            obj.max_sub_brand = plan.max_sub_brand
            obj.max_unit_per_brand = plan.max_unit_per_brand

        super().save_model(request, obj, form, change)

    def calculate_allocation(self, subscription_plan):
        tokens_remaining = self.calculate_tokens(subscription_plan)
        print("Tokens Remaining:", tokens_remaining)
        minutes_remaining = self.calculate_minutes(subscription_plan)
        print("Minutes Remaining:", minutes_remaining)
        classmate_minutes_remaining = self.calculate_classmate_minutes(
            subscription_plan
        )
        print("Classmate Minutes Remaining:", classmate_minutes_remaining)
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


@admin.register(MembershipBonus)
class MembershipBonusAdmin(admin.ModelAdmin):
    list_display = ["token", "minute"]


@admin.register(Invoice)
class MembershipBonusAdmin(admin.ModelAdmin):
    list_display = ["client"]
