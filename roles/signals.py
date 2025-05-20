from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta, datetime
from django.db.models import F, Func, Value, CharField
from django.db.models.functions import Concat
from django.db.models import Q
from roles.models import Role
from report.tasks.periodic.update_assistant_vector_files import evaluate_role_update



@receiver(post_save, sender=Role)
def connect_data_on_save(sender, instance, created, **kwargs):
    if created:
        return

    evaluate_role_update.delay(instance.pk)



    