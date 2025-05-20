from django.db import models

# model for Queue email
class QueueEmail(models.Model):
    STATUS = [
        ('1', "Pending"),
        ('2', "Sent"),
        ('3', "Failed")
    ]
    TYPE = [
        ('1', "default"),
        ('2', "template"),
    ]
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    entry_data = models.JSONField(null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS, default="1")
    type = models.CharField(max_length=50, choices=TYPE, default="default")
    template_id = models.CharField(max_length=255,blank=True,null=True)
    sender_email = models.CharField(max_length=255,blank=True,null=True)


    def __str__(self):
        return f"{self.email} - {self.subject}"