from django.apps import AppConfig



class RolesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "roles"


    def ready(self) -> None:
        from . import signals
        return super().ready()