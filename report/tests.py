from django.test import TestCase
from datetime import datetime
from .models import ResyReservation, ToastOrder
from .signals import update_user


class UpdateUserTestCase(TestCase):
    def test_update_user(self):
        # Create a test reservation
        reservation_date = datetime.now().date()
        reservation_time = datetime.now().time()
        reservation = ResyReservation.objects.create(
            reservation_date=reservation_date,
            time=reservation_time,
            table_name="Table 1",
            user=None  # User is initially None
        )

        # Create a test ToastOrder
        order_date = datetime.now().date()
        order_time = datetime.now().time()
        order = ToastOrder.objects.create(
            opened=order_date.strftime("%A %B %d, %Y"),
            time=order_time.strftime("%I:%M %p"),
            table="Table 1",
            user=None  # User is initially None
        )

        # Call the update_user signal
        update_user(sender=ToastOrder, instance=order, created=True)

        # Check if the user has been updated
        self.assertEqual(reservation.user, order.user)