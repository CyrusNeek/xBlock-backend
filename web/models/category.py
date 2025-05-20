from django.db import models
from django.conf import settings

class CategoryManager(models.Manager):
    def meetings(self):
        return self.filter(type='metting')

    def vtks(self):
        return self.filter(type='vtk')



class Category(models.Model):
    objects = CategoryManager()
    CATEGORY_TYPES = [
        ('meeting', 'Meeting'),
        ('vtk', 'Speech Knowledge'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    is_enabled = models.BooleanField(default=True)  
    priority = models.IntegerField(blank=True, null=True)  
    
    type = models.CharField(
        max_length=20,
        choices=CATEGORY_TYPES,
        default='vtk',  
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_categories",
    )

    class Meta:
        verbose_name = "Category"         
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.title  
