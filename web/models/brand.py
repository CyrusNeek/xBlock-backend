from django.db import models
from django.contrib.auth.models import User
from .brand_owner import BrandOwner


class Brand(models.Model):
    admin_name = models.CharField(max_length=100) # this is just for identifying user brand in admin, not showing to user
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        BrandOwner, on_delete=models.CASCADE, null=True, blank=True, related_name="brands"
    )
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    affiliation = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="sub_brand") # Useless
    brand_image_url = models.TextField(null=True, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name
