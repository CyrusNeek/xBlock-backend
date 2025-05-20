from django.apps import AppConfig


class XmeetingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "xmeeting"

    def ready(self):
        from . import signals
