from django.contrib import admin
from pos.models import (
    Customer,
    DiscountPromotion,
    Inventory,
    Payment,
    RestaurantLocation,
    ShiftDetail,
    Staff,
    TechnicalMetadata,
    TransactionItem,
    Transaction,
)

admin.site.register(Customer)
admin.site.register(DiscountPromotion)
admin.site.register(Inventory)
admin.site.register(Payment)
admin.site.register(RestaurantLocation)
admin.site.register(ShiftDetail)
admin.site.register(Staff)
admin.site.register(TechnicalMetadata)
admin.site.register(TransactionItem)
admin.site.register(Transaction)
