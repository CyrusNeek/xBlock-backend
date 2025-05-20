from report.models import ToastOrder
from report.signals.toast_order_signals import connect_tock_user_on_toast_order
from celery import shared_task


@shared_task
def connect_toasts():
    toasts = ToastOrder.objects.filter(user=None)


    for toast in toasts:
        connect_tock_user_on_toast_order(ToastOrder, toast, True)
    

