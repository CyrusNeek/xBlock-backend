from django.db import models


class WebsiteInteraction(models.Model):
    PAGE_VIEW = "page_view"
    CLICK = "click"
    FORM_SUBMIT = "form_submit"

    INTERACTION_TYPE_CHOICES = [
        (PAGE_VIEW, "Page View"),
        (CLICK, "Click"),
        (FORM_SUBMIT, "Form Submit"),
    ]

    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"

    DEVICE_TYPE_CHOICES = [
        (DESKTOP, "Desktop"),
        (MOBILE, "Mobile"),
        (TABLET, "Tablet"),
    ]

    customer = models.ForeignKey("Customer", on_delete=models.PROTECT)
    session_id = models.CharField(max_length=255)
    page_url = models.URLField()
    interaction_type = models.CharField(max_length=50, choices=INTERACTION_TYPE_CHOICES)
    interaction_date = models.DateField()
    interaction_time = models.TimeField()
    device_type = models.CharField(max_length=50, choices=DEVICE_TYPE_CHOICES)
    browser = models.CharField(max_length=100)
    ip_address = models.TextField()
    notes = models.CharField(max_length=255, blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Interaction {self.pk} by {self.customer}"
