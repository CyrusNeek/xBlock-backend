from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import timedelta
from report.models import ResyReservation, TockBooking, ToastOrder
from django.db.models import Q
from django.utils import timezone


# @receiver(post_save, sender=TockBooking)
# @receiver(post_save, sender=ResyReservation)
# def connect_data_on_save (sender, instance, created, **kwargs):
#     if created:
#         time = instance.datetime if sender is ResyReservation else instance.time
#         if timezone.is_naive(time):
#             time = timezone.make_aware(time)
#         start_time = time - timedelta(minutes=15)
#         end_time = time + timedelta(minutes=40)
        
#         table_values = (
#             (instance.table if sender is ResyReservation else instance.tables)
#             .replace(" ", "")
#             .split(",")
#         )
        
#         query = Q()
#         for table_value in table_values:
#             query |= Q(table=table_value)
        
#         toast_order = (
#             ToastOrder.objects.filter(
#                 opened__range=(start_time, end_time),
#                 toast_auth__unit=(
#                     instance.resy_auth.unit
#                     if sender is ResyReservation
#                     else instance.tock.unit
#                 ),
#                 user=None,  # Only update ToastOrder where user is None
#             )
#             .filter(query)
#             .first()
#         )
        
#         if toast_order:
#             toast_order.user = instance.user
#             toast_order.is_valid = True
#             toast_order.save()
