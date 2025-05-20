from rest_framework import serializers

from report.models.toast_order import ToastOrder
from .report_payment_serializer import PaymentSerializer
from .item_selection_details_serializer import ItemSelectionDetailsSerializer


class ReportOrderSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    toastpayment_set = PaymentSerializer(many=True)
    toastitemselectiondetails_set = ItemSelectionDetailsSerializer(many=True)

    class Meta:
        model = ToastOrder
        fields = [
            "full_name",
            "table",
            "opened",
            "total",
            "amount",
            "id",
            "checks",
            "revenue_center",
            "discount_amount",
            "number_of_guests",
            "tax",
            "tip",
            "gratuity",
            "voided",
            "duration_opened_to_paid",
            "order_source",
            "toastpayment_set",
            "toastitemselectiondetails_set",
            "order_id",
            "order_number",
            "server",
        ]

    def get_full_name(self, obj):
        # Assuming that Guest has a full_name method to combine first and last name
        guest_profile = obj.guest_profiles.first()
        if guest_profile and guest_profile.user:
            return guest_profile.user.full_name
        return "Unknown Guest"