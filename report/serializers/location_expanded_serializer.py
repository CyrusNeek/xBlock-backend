from rest_framework import serializers

from report.models import ReportLocation, TockAuth, TockBooking
from report.models.resy_reservation import ResyReservation
from report.serializers.resy_reservation_serializer import ResyReservationSerializer
from report.serializers.tock_booking_serializer import TockBookingSerializer
from web.models import Unit


class ReportUnitSerializer(serializers.ModelSerializer):
    bookings = serializers.SerializerMethodField()
    reservations = serializers.SerializerMethodField()

    class Meta:
        fields = ["name", "id", "address", "reservations", "bookings"]
        model = Unit

    def get_bookings(self, unit):
        # Retrieve the pre-calculated Tock IDs from the context
        tocks_id = self.context.get("tocks_id")

        # Fetch Tock bookings using the IDs already available in the context
        tock_bookings = TockBooking.objects.filter(
            tock__unit=unit,
            id__in=tocks_id
        )

        return TockBookingSerializer(tock_bookings, many=True).data

    def get_reservations(self, unit):
        # Retrieve the pre-calculated Resy IDs from the context
        resy_id = self.context.get("resy_id")

        # Fetch Resy reservations using the IDs already available in the context
        resy_reservations = ResyReservation.objects.filter(
            resy_auth__unit=unit,
            id__in=resy_id
        )

        return ResyReservationSerializer(resy_reservations, many=True).data
