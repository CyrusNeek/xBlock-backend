from report.models import ToastOrder
from django.db.models import Q
import django_filters
from django_filters import filters
from django_filters.filterset import FilterSet

class ToastOrderFilter(FilterSet):
    from_date = django_filters.DateFilter(field_name="opened", lookup_expr="gte")
    to_date = django_filters.DateFilter(field_name="opened", lookup_expr="lte")
    user_id = filters.NumberFilter(method="filter_user_id")
    tag_ids = filters.CharFilter(method="filter_tag_ids")
    location_ids = filters.CharFilter(method="filter_location_ids")

    class Meta:
        model = ToastOrder
        fields = ["from_date", "to_date"]

    def filter_user_id(self, queryset, name, value):
        """
        Filter by the user_id provided in query params.
        Matches the guest profile's user ID.
        """
        return queryset.filter(guest_profiles__user__id=value)

    def filter_tag_ids(self, queryset, name, value):
        """
        Filter by tag IDs, applied on TockBooking or ResyReservation tags.
        """
        tag_ids = value.split(",")
        return queryset.filter(
            Q(guest_profiles__toast__tockbooking__tags__id__in=tag_ids) |
            Q(guest_profiles__toast__resyreservation__guest_tags__id__in=tag_ids)
        ).distinct()

    def filter_location_ids(self, queryset, name, value):
        """
        Filter by location IDs, applied to both TockBooking and ResyReservation units.
        """
        location_ids = value.split(",")
        return queryset.filter(
            Q(guest_profiles__toast__tockbooking__tock__unit__in=location_ids) |
            Q(guest_profiles__toast__resyreservation__resy_auth__unit__in=location_ids)
        ).distinct()
