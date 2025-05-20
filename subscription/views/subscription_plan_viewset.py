from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from subscription.models import SubscriptionPlan
from web.models import BrandOwner
from subscription.serializers import SubscriptionPlanSerializer
from django.utils.timezone import now


class SubscriptionPlanViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """
    ViewSet for listing SubscriptionPlans.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionPlanSerializer
    
    now = now()
    
    queryset = SubscriptionPlan.objects.filter(
        status="active",
        start_time__lte=now,
        end_time__gte=now
    ).all()

    def get_permissions(self):
        user_id = self.request.user.id
        permissions = super().get_permissions()
        
        if not BrandOwner.objects.filter(users=user_id).exists():
            raise PermissionDenied({"detail": "You do not have permission to access subscription plans."})
        
        return permissions