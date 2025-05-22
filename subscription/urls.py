from rest_framework.routers import DefaultRouter
from .views import (
    SubscriptionPlanViewSet,
    UserPlanViewSet,
    RefreshAllocationAPIView,
    MeetingAllocationAPIView,
    WebhookReceivedView,
    InvoiceViewSet,
    CreateCustomerPortalSessionView
)

from django.urls import path

router = DefaultRouter()

router.register(r"plans", SubscriptionPlanViewSet, basename="plans")
router.register(r"user-plans", UserPlanViewSet, basename="user-plans")
router.register(r"invoice", InvoiceViewSet, basename="invoice")

urlpatterns = [
    path('create-customer-portal-session/', CreateCustomerPortalSessionView.as_view(), name='create_customer_portal_session'),   
    path('meeting-allocation/', MeetingAllocationAPIView.as_view(),
         name='meeting-allocation'),
    path('webhook/', WebhookReceivedView.as_view(), name='webhook'),
] + router.urls
