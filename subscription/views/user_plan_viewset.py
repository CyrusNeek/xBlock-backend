from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from subscription.models import UserSubscription
from web.models import BrandOwner, User
from subscription.serializers import UserSubscriptionSerializer
from django.db.models import Case, When, Value, IntegerField


class UserPlanViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """
    ViewSet for listing, and retrieving UserSubscriptions.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserSubscriptionSerializer

    def get_queryset(self):
        user_id = self.request.user.pk
        user = User.objects.get(pk=user_id)

        return (
            UserSubscription.objects.filter(brand_owner=user.affiliation)
            .select_related('brand_owner')
            .annotate(
                status_priority=Case(
                    When(status=UserSubscription.ACTIVE, then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField(),
                )
            )
            .order_by("status_priority", "-start_date")
        )

    def get_permissions(self):
        user_id = self.request.user.id
        # if not BrandOwner.objects.filter(users__id=user_id).exists():
        #     raise PermissionDenied(
        #         {"detail": "You do not have permission to access user plans."}
        #     )
        return super().get_permissions()
