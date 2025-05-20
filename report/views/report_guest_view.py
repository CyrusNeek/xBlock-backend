import logging
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from report.filters.report_guest_filter import ReportGuestFilter
from report.models.guest_profile import Guest, GuestProfile
from report.models.toast_order import ToastOrder
from report.models.tock_booking import TockBooking
from report.pagination import StandardResultsSetPagination
from report.serializers import (
    ReportGuestSerializer,
    ReportGuestActivitySerializer,
    ReportUnitSerializer,
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework import status
from web.models.unit import Unit
from .export_csv_view import CSVExportMixin
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from report.models import ReportUser
from django.db.models.functions import Concat
from django.db.models import (
    Value,
    CharField,
    IntegerField,
    Max,
    Min,
    Avg,
    Sum,
    Count,
    Case,
    When,
    F,
    Q,
    DecimalField,
    FloatField,
    Subquery,
)
from django.db.models.expressions import OuterRef
from roles.constants import LIMITED_GUEST_PROFILE_ACCESS, UNLIMITED_GUEST_PROFILE_ACCESS
from roles.permissions import UserPermission
from django.db.models.functions import Coalesce
from django.core.cache import cache

logger = logging.getLogger(__name__)


# class ReportGuestView1(ListAPIView, RetrieveAPIView, CSVExportMixin, GenericViewSet):
#     serializer_class = ReportGuestSerializer
#     pagination_class = StandardResultsSetPagination
#     permission_classes = [UserPermission, IsAuthenticated]
#     required_permission = [LIMITED_GUEST_PROFILE_ACCESS,
#                            UNLIMITED_GUEST_PROFILE_ACCESS]
#     filter_backends = [DjangoFilterBackend,
#                        OrderingFilter, filters.SearchFilter]
#     filterset_class = ReportGuestFilter

#     csv_filename = "report_guests.csv"
#     search_fields = ["email", "phone", "annotated_full_name"]

#     csv_headers = ["email", "phone", "full_name"]

#     distinct_toastorder_totals = ToastOrder.objects.filter(
#         user__pk=OuterRef('pk')
#     ).values('user__pk').annotate(
#         total=Sum('total')
#     ).values('total')

#     distinct_toastorder_avgs = ToastOrder.objects.filter(
#         user__pk=OuterRef('pk')
#     ).values('user__pk').annotate(
#         avg=Avg('total')
#     ).values('avg')

#     def get_queryset(self):
#         user = self.request.user
#         cached_queryset = cache.get(f"report_guest_queryset_{user.pk}")
#         if cached_queryset:
#             return cached_queryset

#         user = user.__class__.objects.prefetch_related(
#             'affiliation__brands',
#             'units'
#         ).select_related('affiliation').get(pk=user.pk)

#         # queryset = super().get_queryset()
#         # Fetch the user with related data

#         queryset = ReportUser.objects.annotate(
#             lifetime_value=Coalesce(
#                 Subquery(self.distinct_toastorder_totals,
#                          output_field=DecimalField()),
#                 Value(0, output_field=DecimalField()),
#                 output_field=DecimalField()
#             ),
#             avg_check=Coalesce(
#                 Subquery(self.distinct_toastorder_avgs,
#                          output_field=DecimalField()),
#                 Value(0, output_field=DecimalField()),
#                 output_field=DecimalField()
#             ),
#             total_orders_count=Coalesce(
#                 Count("toastorder__id", distinct=True,
#                       output_field=IntegerField()),
#                 Value(0, output_field=IntegerField()),
#                 output_field=IntegerField()
#             ),
#             tag_count=Coalesce(
#                 Count("tockbooking__id", distinct=True,
#                       output_field=IntegerField()),
#                 Value(0, output_field=IntegerField()),
#                 output_field=IntegerField()
#             ),
#             visits=Coalesce(
#                 Count(
#                     "tockbooking__id",
#                     filter=Q(
#                         tockbooking__status=TockBooking.BookStatus.BOOKED.value),
#                     distinct=True, output_field=IntegerField()
#                 ) +
#                 Count(
#                     "toastorder__id",
#                     distinct=True, output_field=IntegerField()
#                 ),
#                 Value(0, output_field=IntegerField()),
#                 output_field=IntegerField()
#             ),
#             cancellations=Coalesce(
#                 Count("tockbooking__id", filter=Q(tockbooking__status=TockBooking.BookStatus.CANCELED.value),
#                       distinct=True, output_field=IntegerField()),
#                 Value(0, output_field=IntegerField()),
#                 output_field=IntegerField()
#             ),
#             no_shows=Coalesce(
#                 Count("tockbooking__id", filter=Q(tockbooking__status=TockBooking.BookStatus.NO_SHOW.value),
#                       distinct=True, output_field=IntegerField()),
#                 Value(0, output_field=IntegerField()),
#                 output_field=IntegerField()
#             ),
#             annotated_full_name=Concat(
#                 "first_name", Value(" "), "last_name", output_field=CharField()
#             )
#         ).order_by('id').distinct()
#         units = user.all_units
#         q = queryset.filter(brand__units__in=units)
#         # Cache for 15 minutes
#         cache.set(f"report_guest_queryset_{user.pk}", q, 60 * 15)
#         return q
#         # log query
#         # if UserPermission.check_user_permission(user, UNLIMITED_GUEST_PROFILE_ACCESS):
#         #     brands = user.affiliation.brands.all()
#         #     q = queryset.filter(brand__in=brands)
#         #     return q

#         # elif UserPermission.check_user_permission(user, LIMITED_GUEST_PROFILE_ACCESS):
#         #     units = user.all_units
#         #     q = queryset.filter(brand__units__in=units)
#         #     return q

#         return queryset.none()

#     @action(detail=False, methods=["get"], url_path="export-csv", url_name="export_csv")
#     def export_csv(self, request, *args, **kwargs):
#         return super().export_csv(request, *args, **kwargs)

#     @action(detail=False, methods=["get"], url_path="stats", url_name="guests-stats")
#     def stats(self, request):
#         # queryset = self.get_queryset()
#         # stats = queryset.aggregate(
#         #     max_avg_check=Max("avg_check"),
#         #     min_avg_check=Min("avg_check"),
#         #     max_lifetime_value=Max("lifetime_value"),
#         #     min_lifetime_value=Min("lifetime_value"),
#         #     max_tip=Max("toastorder__tip"),
#         #     min_tip=Min("toastorder__tip"),
#         #     # avg_tip=Avg('toastpayment__tip')
#         # )
#         # return Response(stats, status=status.HTTP_200_OK)
#         return Response([], status=status.HTTP_200_OK)


class ReportGuestView(ListAPIView, RetrieveAPIView, CSVExportMixin, GenericViewSet):
    serializer_class = ReportGuestSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [UserPermission, IsAuthenticated]
    required_permission = [LIMITED_GUEST_PROFILE_ACCESS,
                           UNLIMITED_GUEST_PROFILE_ACCESS]
    filter_backends = [DjangoFilterBackend,
                       OrderingFilter, filters.SearchFilter]
    filterset_class = ReportGuestFilter

    csv_filename = "report_guests.csv"
    search_fields = ["email", "phone", "first_name", "last_name"]

    csv_headers = ["email", "phone", "full_name","lifetime_value", "avg_check","total_orders_count"]

    def get_queryset(self):
        user = self.request.user
        user = user.__class__.objects.prefetch_related(
            'affiliation__brands',
            'units'
        ).select_related('affiliation').get(pk=user.pk)

        queryset = Guest.objects.prefetch_related(
            'profiles__toast'  # Prefetch toast orders related to guest profiles
        ).annotate(
            avg_check=Avg('profiles__toast__total'),
            lifetime_value=Sum('profiles__toast__total'),
            total_orders_count=Count('profiles__toast__id'),
            lifetime_order=Case(
                When(lifetime_value__isnull=True, then=Value(1)),
                When(lifetime_value=0.0, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        ).order_by('lifetime_order', '-lifetime_value')

        if UserPermission.check_user_permission(user, UNLIMITED_GUEST_PROFILE_ACCESS):
            brands = user.affiliation.brands.all()
            queryset = queryset.filter(brand__in=brands)
            return queryset

        elif UserPermission.check_user_permission(user, LIMITED_GUEST_PROFILE_ACCESS):
            units = user.all_units
            queryset = queryset.filter(brand__units__in=units)
            return queryset
        return queryset.none()

    @action(detail=False, methods=["get"], url_path="export-csv", url_name="export_csv")
    def export_csv(self, request, *args, **kwargs):
        return super().export_csv(request, *args, **kwargs)

    @action(detail=False, methods=["get"], url_path="stats", url_name="guests-stats")
    def stats(self, request):
        # Get the basic queryset for guests
        guest_queryset = self.get_queryset()

        # Calculate tip statistics directly from ToastOrder (faster than going through GuestProfile)
        toast_tip_stats = ToastOrder.objects.aggregate(
            max_tip=Max('tip'),
            min_tip=Min('tip'),
            avg_tip=Avg('tip')
        )

        # You can still calculate other stats based on guests if needed
        guest_stats = guest_queryset.aggregate(
            max_avg_check=Max("avg_check"),
            min_avg_check=Min("avg_check"),
            max_lifetime_value=Max("lifetime_value"),
            min_lifetime_value=Min("lifetime_value"),
        )

        # Combine the stats from both queries
        stats = {**guest_stats, **toast_tip_stats}

        return Response(stats, status=status.HTTP_200_OK)


class ReportUserActivityViewSet1(ReadOnlyModelViewSet):
    distinct_toastorder_totals = ToastOrder.objects.filter(
        user__pk=OuterRef('pk')
    ).values('user__pk').annotate(
        total=Sum('total')
    ).values('total')

    distinct_toastorder_avgs = ToastOrder.objects.filter(
        user__pk=OuterRef('pk')
    ).values('user__pk').annotate(
        avg=Avg('total')
    ).values('avg')

    queryset = ReportUser.objects.annotate(
        lifetime_value=Coalesce(
            Subquery(distinct_toastorder_totals, output_field=DecimalField()),
            Value(0, output_field=DecimalField()),
            output_field=DecimalField()
        ),
        avg_check=Coalesce(
            Subquery(distinct_toastorder_avgs, output_field=DecimalField()),
            Value(0, output_field=DecimalField()),
            output_field=DecimalField()
        ),
        total_orders_count=Coalesce(
            Count("toastorder__id", distinct=True,
                  output_field=IntegerField()),
            Value(0, output_field=IntegerField()),
            output_field=IntegerField()
        ),
        tag_count=Coalesce(
            Count("tockbooking__id", distinct=True,
                  output_field=IntegerField()),
            Value(0, output_field=IntegerField()),
            output_field=IntegerField()
        ),
        # Counting visits from both TockBooking and ToastOrder
        visits=Coalesce(
            Count(
                "tockbooking__id",
                filter=Q(tockbooking__status=TockBooking.BookStatus.BOOKED.value),
                distinct=True, output_field=IntegerField()
            ) +
            Count(
                "toastorder__id",
                distinct=True, output_field=IntegerField()
            ),
            Value(0, output_field=IntegerField()),
            output_field=IntegerField()
        ),
        cancellations=Coalesce(
            Count("tockbooking__id", filter=Q(tockbooking__status=TockBooking.BookStatus.CANCELED.value),
                  distinct=True, output_field=IntegerField()),
            Value(0, output_field=IntegerField()),
            output_field=IntegerField()
        ),
        no_shows=Coalesce(
            Count("tockbooking__id", filter=Q(tockbooking__status=TockBooking.BookStatus.NO_SHOW.value),
                  distinct=True, output_field=IntegerField()),
            Value(0, output_field=IntegerField()),
            output_field=IntegerField()
        ),
        annotated_full_name=Concat(
            "first_name", Value(" "), "last_name", output_field=CharField()
        )
    ).order_by("id")

    serializer_class = ReportGuestActivitySerializer

    def get_queryset(self):
        user = self.request.user

        user_brands = user.units.values_list("brand", flat=True)

        brand = None if user.unit is None else user.unit.brand

        return super().get_queryset().filter(Q(brand__in=user_brands) | Q(brand=brand))


class ReportUserActivityViewSet(ReadOnlyModelViewSet):
    serializer_class = ReportGuestActivitySerializer
    queryset = Guest.objects.annotate(
        lifetime_order=Case(
            When(Lifetime_value__gt=0, then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        )
    ).order_by('-lifetime_order', '-Lifetime_value')

    def get_queryset(self):
        # Get the currently logged-in user
        user = self.request.user

        # Get the user's brands from the units they are affiliated with
        user_brands = user.units.values_list("brand", flat=True)

        # Check the current unit's brand if the user is associated with a single unit
        brand = None if user.unit is None else user.unit.brand

        # Filter the guests by the brands the user has access to
        return super().get_queryset().filter(
            Q(brand__in=user_brands) | Q(brand=brand)
        )


class ReportUserInfoView(ListAPIView):
    queryset = Unit.objects.all()
    serializer_class = ReportUnitSerializer

    def get_queryset(self):
        user = self.request.user
        try:
            guest = Guest.objects.get(pk=self.kwargs["pk"])
        except Guest.DoesNotExist:
            return Unit.objects.none()
        guest_profiles = GuestProfile.objects.filter(user=guest)
        tocks_id = guest_profiles.filter(model_name=GuestProfile.TOCK).values_list("object_id", flat=True)
        resy_id = guest_profiles.filter(model_name=GuestProfile.RESY).values_list("object_id", flat=True)
        # Return all units that have associated reservations in Tock or Resy for this guest
        return Unit.objects.filter(
            Q(tock_auth__tockbooking__id__in=tocks_id)
            | Q(resy_auth__resyreservation__id__in=resy_id)
        ).distinct()
    
    
    def get_serializer_context(self):
        """
        Pass the guest and reservation ids to the serializer context.
        """
        context = super().get_serializer_context()
        guest = Guest.objects.get(pk=self.kwargs["pk"])
        guest_profiles = GuestProfile.objects.filter(user=guest)

        # Retrieve tocks and resy IDs only once, and pass them to the serializer
        context["tocks_id"] = guest_profiles.filter(model_name=GuestProfile.TOCK).values_list("object_id", flat=True)
        context["resy_id"] = guest_profiles.filter(model_name=GuestProfile.RESY).values_list("object_id", flat=True)
        return context