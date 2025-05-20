from rest_framework import serializers
from report.models import ToastItemSelectionDetails


class ItemSelectionDetailsSerializer(serializers.ModelSerializer):

  class Meta:
    fields = ['order_date', 'server', 'table', 'id', 'service', 'dining_option', 'item_selection_id', 'net_price', 'gross_price',
    'menu_item', 'discount', 'tax', 'quantity', 'void', 'tax_exempt', 'tab_name', 'toast']
    model  = ToastItemSelectionDetails