from django.db import models
from django.utils.timezone import now

class Customer(models.Model):
    # Basic customer information
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Meta class to define ordering and verbose name
    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        constraints = [
            models.UniqueConstraint(fields=["first_name", "last_name", "email", "phone_number"], name='unique_name_email_phone')
        ]

    # String representation of the Customer model
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    def name(self):
        return f"{self.first_name} {self.last_name}"
    
