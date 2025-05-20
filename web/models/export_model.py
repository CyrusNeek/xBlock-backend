from django.db import models
from django.conf import settings



class ExportModel(models.Model):
    EXPORT_MODEL_TYPES = [
        ('meeting', 'Meeting'),
        ('vtk', 'Speech Knowledge'),
    ]

    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200,default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    prompt = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    output_format = models.TextField(blank=True) 
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    is_enabled = models.BooleanField(blank=True)
    priority = models.IntegerField(blank=True, null=True)  

    type = models.CharField(
        max_length=20,
        choices=EXPORT_MODEL_TYPES,
        default='vtk',  
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_export_models",
    )
    content = models.TextField(blank=True)



    def __str__(self):
        return self.title
