from django.apps import AppConfig


class ReportConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "report"


    def ready(self) -> None:
        from . import signals
        
        return super().ready()
