from django.db import models
# from web.models import Brand, User

class UserBrand(models.Model):
    user = models.ForeignKey("User", related_name='user_brands', on_delete=models.CASCADE)
    brand = models.ForeignKey("Brand", related_name='user_brands', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'brand')

    def __str__(self):
        return f"{self.brand.name} {self.user.name}"