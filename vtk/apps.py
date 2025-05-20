from django.apps import AppConfig


class VTKConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "vtk"
    
    def ready(self):
        from . import signals