from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Q
from django.utils.timezone import timedelta

from report.models import ToastOrder, ResyReservation, TockBooking


# TODO: Change structure important

# @receiver(post_save, sender=ToastOrder)
# def connect_tock_user_on_toast_order(sender, instance, created, **kwargs):
#     if created is False or not instance.table:
#         return
    
#     if timezone.is_naive(instance.opened):
#         instance.opened = timezone.make_aware(instance.opened)

#     start_time = instance.opened - timedelta(minutes=40)
#     end_time = instance.opened + timedelta(minutes=15)
    
#     try:
#         table_str = str(instance.table).replace('.0', '')  # Remove decimal point if present
#         table_int = int(float(table_str))
#         table_str = str(table_int)
#     except:
#         table_str = instance.table
        
#     tock_bookings = (
#         TockBooking.objects.filter(tock__unit=instance.toast_auth.unit)
#         .filter(Q(time__gte=start_time) & Q(time__lte=end_time) & Q(status="Booked"))
#         .filter(
#             Q(tables__contains=f", {table_str},") |
#             Q(tables__contains=f",{table_str},") |
#             Q(tables__startswith=f"{table_str},") |
#             Q(tables__startswith=f"{table_str}, ") |
#             Q(tables__endswith=f",{table_str}") |
#             Q(tables__endswith=f", {table_str}") |
#             Q(tables=table_str)
#         )
#         .first()
#     )
#     if tock_bookings:
#         print(f"updated : {tock_bookings.id}")
#         instance.user = tock_bookings.user
#         instance.is_valid = True
#         instance.save()


# @receiver(post_save, sender=ToastOrder)
# def connect_resy_user_on_toast_order(sender, instance, created, **kwargs):
#     if not created or not instance.table:
#         return

#     # Ensure instance.opened is timezone-aware
#     if timezone.is_naive(instance.opened):
#         instance.opened = timezone.make_aware(instance.opened)

#     start_time = instance.opened - timedelta(minutes=40)
#     end_time = instance.opened + timedelta(minutes=15)

#     reservation_query = (
#         ResyReservation.objects.filter(
#             resy_auth__unit=instance.toast_auth.unit,
#             datetime__range=(start_time, end_time),
#             table__icontains=instance.table
#         )
#         .first()
#     )

#     if reservation_query:
#         instance.user = reservation_query.user
#         instance.is_valid = True
#         instance.save()
