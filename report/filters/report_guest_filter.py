from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from report.models import ReportUser
from django_filters import filters
from django_filters.filterset import FilterSet
from django.db.models import Q


import logging

from report.models.guest_profile import Guest

logger = logging.getLogger(__name__)


class ReportGuestFilter(FilterSet):
    min_lifetime_value = filters.NumberFilter(
        field_name="lifetime_value", lookup_expr="gte"
    )
    max_lifetime_value = filters.NumberFilter(
        field_name="lifetime_value", lookup_expr="lte"
    )
    min_avg_check = filters.NumberFilter(
        field_name="avg_check", lookup_expr="gte")
    max_avg_check = filters.NumberFilter(
        field_name="avg_check", lookup_expr="lte")
    tag_ids = filters.CharFilter(method="filter_tag_ids")
    location_ids = filters.CharFilter(method="filter_location_ids")

    class Meta:
        model = Guest
        fields = []

    def filter_tag_ids(self, queryset, name, value):
        tag_ids = value.split(",")

        # Ensure filtering on both TockBooking and ResyReservation based on tags
        return queryset.filter(
            Q(profiles__toast__guest_profiles__toast__tockbooking__tags__id__in=tag_ids)
            # Q(profiles__toast__guest_profiles__toast__resyreservation__guest_tags__id__in=tag_ids)
        ).distinct()

    def filter_location_ids(self, queryset, name, value):
        location_ids = value.split(",")

        # Ensure filtering on both TockBooking and ResyReservation based on location
        return queryset.filter(
            Q(profiles__toast__guest_profiles__toast__resyreservation__resy_auth__unit__in=location_ids) |
            Q(profiles__toast__guest_profiles__toast__tockbooking__tock__unit__in=location_ids)
        ).distinct()
