from rest_framework import serializers
from report.models import ToastOrder, ReportUser, Tag, ToastPayment, ReportLocation
from django.db.models import Sum, Avg, Q, Count


from report.models.guest_profile import Guest, GuestProfile
from report.models.resy_reservation import ResyReservation
from report.models.tock_booking import TockBooking


class ReportGuestSerializer1(serializers.ModelSerializer):
    tag_count = serializers.IntegerField()
    avg_check = serializers.FloatField()
    lifetime_value = serializers.FloatField()
    total_orders_count = serializers.IntegerField(default=0)

    class Meta:
        model = ReportUser
        fields = [
            "email",
            "phone",
            "full_name",
            "tag_count",
            "avg_check",
            "lifetime_value",
            "id",
            "total_orders_count",
        ]


class ReportGuestSerializer(serializers.ModelSerializer):
    # tag_count = serializers.IntegerField()
    avg_check = serializers.FloatField()
    lifetime_value = serializers.FloatField()
    total_orders_count = serializers.IntegerField(default=0)

    class Meta:
        model = Guest
        fields = [
            "email",
            "phone",
            "full_name",
            # "tag_count",
            "avg_check",
            "lifetime_value",
            "id",
            "total_orders_count",
        ]

    def get_avg_check(self, obj):
        # Return the average check (order amount) for this guest
        return obj.avg_check if obj.avg_check else 0.0

    def get_lifetime_value(self, obj):
        # Return the lifetime value (sum of total_price from GuestProfile)
        return obj.lifetime_value if obj.lifetime_value else 0.0


class ReportGuestActivitySerializer(serializers.ModelSerializer):
    visits = serializers.SerializerMethodField()
    cancellations = serializers.SerializerMethodField()
    no_shows = serializers.SerializerMethodField()
    blocked_by = serializers.SerializerMethodField()
    orders_count_by_location = serializers.SerializerMethodField()

    class Meta:
        model = Guest
        fields = [
            "id",
            "email",
            "phone",
            "first_name",
            "last_name",
            "brand",
            "visits",
            "cancellations",
            "no_shows",
            "blocked_by",
            "orders_count_by_location",
        ]


    def get_visits(self, obj):
        """
        Count the number of ToastOrder records related to this guest via GuestProfile.
        """
        guest_profiles = GuestProfile.objects.filter(user=obj)

        # Count the number of distinct ToastOrder records associated with the guest's profiles
        # total_visits = ToastOrder.objects.filter(
        #     guest_profiles__in=guest_profiles).count()

        return guest_profiles.count()

    def get_cancellations(self, obj):
        """
        Filter GuestProfiles for this guest and handle both TockBooking and ResyReservation cancellations.
        """
        guest_profiles = GuestProfile.objects.filter(user=obj)

        # Fetch cancellations from TockBooking
        tock_cancellations = TockBooking.objects.filter(
            id__in=guest_profiles.filter(
                model_name='Tock').values_list('object_id', flat=True),
            status='Canceled'
        ).count()

        # Fetch cancellations from ResyReservation
        resy_cancellations = ResyReservation.objects.filter(
            id__in=guest_profiles.filter(
                model_name='Resy').values_list('object_id', flat=True),
            status='Canceled'
        ).count()

        return tock_cancellations + resy_cancellations

    def get_no_shows(self, obj):
        """
        Filter GuestProfiles for this guest and handle both TockBooking and ResyReservation no-shows.
        """
        guest_profiles = GuestProfile.objects.filter(user=obj)

        # Fetch no-shows from TockBooking
        tock_no_shows = TockBooking.objects.filter(
            id__in=guest_profiles.filter(
                model_name='Tock').values_list('object_id', flat=True),
            status='No Show'
        ).count()

        # Fetch no-shows from ResyReservation
        resy_no_shows = ResyReservation.objects.filter(
            id__in=guest_profiles.filter(
                model_name='Resy').values_list('object_id', flat=True),
            status='No Show'
        ).count()

        return tock_no_shows + resy_no_shows

    def get_orders_count_by_location(self, obj):
        """
        Count orders by location for this guest from both TockBooking and ResyReservation.
        """
        guest_profiles = GuestProfile.objects.filter(user=obj)

        # Orders for TockBooking
        tock_orders = (
            ToastOrder.objects.filter(
                guest_profiles__in=guest_profiles.filter(model_name='Tock'))
            .values("toast_auth__unit__name")
            .annotate(order_count=Count("id"))
        )

        # Orders for ResyReservation
        resy_orders = (
            ToastOrder.objects.filter(
                guest_profiles__in=guest_profiles.filter(model_name='Resy'))
            .values("toast_auth__unit__name")
            .annotate(order_count=Count("id"))
        )

        # Combine the results for both
        all_orders = list(tock_orders) + list(resy_orders)

        # Prepare the data to return
        data = [
            {
                "unit_name": order["toast_auth__unit__name"],
                "order_count": order["order_count"],
            }
            for order in all_orders
        ]

        return data

    def get_blocked_by(self, obj):
        # Placeholder logic; replace with actual blocked_by logic
        return []  # Adjust this based on the actual blocked_by field
