from rest_framework.generics import ListAPIView
from report.models import ToastOrder
from roles.constants import UNLIMITED_ORDER_INFO_ACCESS, LIMITED_ORDER_INFO_ACCESS
from roles.permissions import UserPermission
from rest_framework.permissions import IsAuthenticated
from report.pagination import StandardResultsSetPagination
from report.serializers import ReportOrderSerializer
from django.utils.dateparse import parse_date
from django_filters.rest_framework import DjangoFilterBackend
from report.filters import ToastOrderFilter
from report.views.export_csv_view import CSVExportMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from web.models import Unit
from django.db.models import Case, When, Value, IntegerField, Q


class ReportOrdersView(ListAPIView, CSVExportMixin, GenericViewSet):
    serializer_class = ReportOrderSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, UserPermission]
    required_permission = [
        UNLIMITED_ORDER_INFO_ACCESS, LIMITED_ORDER_INFO_ACCESS
    ]

    # Base queryset with related models preloaded
    queryset = ToastOrder.objects.select_related("toast_auth__unit") \
        .prefetch_related("toastpayment_set", "toastitemselectiondetails_set", "guest_profiles__user") \
        .annotate(
            has_guest=Case(
                When(guest_profiles__user__isnull=False, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            )
    ).order_by("-has_guest", "-opened")

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ToastOrderFilter
    search_fields = [
        "guest_profiles__user__first_name",
        "guest_profiles__user__last_name",
        "table",
        "opened",
        "total",
        "amount",
        "id",
    ]

    csv_filename = "report_orders.csv"
    csv_headers = ["full_name", "table", "opened", "total", "amount", "id"]

    def get_queryset(self):
        """
        Customizes the queryset based on user permissions, user_id, and optional date filters.
        """
        user = self.request.user

        # Get user permissions and filter by access level
        if UserPermission.check_user_permission(user, UNLIMITED_ORDER_INFO_ACCESS):
            # Unlimited access: filter by the user's brands
            brands = user.affiliation.brands.all()
            queryset = self.queryset.filter(guest_profiles__user__brand__in=brands)

        elif UserPermission.check_user_permission(user, LIMITED_ORDER_INFO_ACCESS):
            # Limited access: filter by units accessible by the user
            units = Unit.objects.accessible_by_user(user)
            queryset = self.queryset.filter(toast_auth__unit__in=units)
        else:
            return self.queryset.none()

        # Optional date filtering (from_date and to_date)
        from_date = self.request.query_params.get("from_date")
        to_date = self.request.query_params.get("to_date")

        if from_date:
            from_date = parse_date(from_date)
            queryset = queryset.filter(opened__gte=from_date)

        if to_date:
            to_date = parse_date(to_date)
            queryset = queryset.filter(opened__lte=to_date)

        return queryset

    @action(detail=False, methods=["get"], url_path="export-csv", url_name="export_csv")
    def export_csv(self, request, *args, **kwargs):
        """
        Exports the filtered queryset to CSV format.
        """
        return super().export_csv(request, *args, **kwargs)