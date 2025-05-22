from pydantic import PlainSerializer
from rest_framework import serializers

# from roles import serilalizers
from subscription.models import SubscriptionPlan, UserSubscription, Invoice


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = [
            "pk",
            "name",
            "start_time",
            "end_time",
            "total_token_allocation",
            "token_user_limit",
            "token_usage_period",
            "daily_token_limit",
            "total_meeting_duration",
            "meeting_session_length",
            "meeting_user_limit",
            "meeting_usage_period",
            "daily_meeting_limit",
            "total_classmate_session_duration",
            "classmate_user_limit",
            "classmate_usage_period",
            "stk_session_length",
            "daily_stk_limit",
            "total_upload_allocation",
            "upload_user_limit",
            "upload_usage_period",
            "daily_upload_limit",
            "subscription_price",
            "total_integration",
            "discount_rate",
            "flat_fee",
            "billing_cycle",
            "subscription_length_days",
            "status",
            "support_level",
            "features_included",
            "max_sub_brand",
            "max_unit_per_brand",
            "image_url"
        ]


class UserSubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = [
            "pk",
            "name",
            "total_token_allocation",
            "token_user_limit",
            "token_usage_period",
            "daily_token_limit",
            "total_meeting_duration",
            "meeting_session_length",
            "meeting_user_limit",
            "meeting_usage_period",
            "daily_meeting_limit",
            "total_classmate_session_duration",
            "classmate_user_limit",
            "classmate_usage_period",
            "stk_session_length",
            "daily_stk_limit",
            "total_upload_allocation",
            "upload_user_limit",
            "upload_usage_period",
            "daily_upload_limit",
            "subscription_price",
            "total_integration",
            "discount_rate",
            "flat_fee",
            "billing_cycle",
            "subscription_length_days",
            "support_level",
            "features_included",
            "max_sub_brand",
            "max_unit_per_brand",
            "image_url"
        ]


class UserSubscriptionSerializer(serializers.ModelSerializer):

    brand_owner = serializers.CharField(read_only=True)
    plan = UserSubscriptionPlanSerializer(read_only=True)

    class Meta:
        model = UserSubscription
        fields = [
            "pk",
            "plan",  
            "start_date",  
            "end_date",  
            "token_remaining",  
            "token_user_limit",  
            "total_tokens",
            "meeting_remaining",  
            "meeting_user_limit",  
            "total_minutes",  
            "classmate_time_remaining",  
            "classmate_user_limit",  
            "total_classmate_minutes",  
            "upload_user_limit",  
            "upload_size_remaining",  
            "total_upload_size",  
            "total_integration",  
            "status",  
            "max_sub_brand",  
            "max_unit_per_brand",
             "brand_owner",
        ]


class InvoiceSerializer(serializers.ModelSerializer):
    subscription = serializers.CharField()

    class Meta:
        model = Invoice
        fields = [
            "id",
            "service",
            # "payload",
            # "client",
            "created_at",
            "invoice_datetime",
            "subscription",
            "payment_status",
            "customer",
            "customer_email",
            "customer_phone",
            "invoice_pdf",
            "hosted_invoice_url",
            "number",
            "period_start",
            "period_end",
            "tax",
            "total",
        ]
