from rest_framework import serializers

from report.models import ToastPayment


class PaymentSerializer(serializers.ModelSerializer):
  tax = serializers.CharField(source="order.tax")
  voided = serializers.BooleanField(source="order.voided")
  
  class Meta:
    fields = ['payment_id', 'paid_date', 'order_date', 'check_id', 'check_number', 'tab_name', 'server', 'table', 'total', 'tip', 'amount', 'service', 'voided', 'tax']
    model = ToastPayment
