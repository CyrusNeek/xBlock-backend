from django.db import models
from .resy_auth import ResyAuth

from .tag import Tag
from report.models.report_user import ReportUser


class ResyRating(models.Model):
    review_date = models.DateField(null=True, blank=True)
    guest = models.CharField(max_length=100)
    vip = models.CharField(max_length=10, blank=True)
    visit_date = models.DateField(null=True, blank=True)
    party_size = models.PositiveIntegerField(null=True, blank=True)
    email = models.EmailField()
    server = models.CharField(max_length=100, blank=True)
    ratings = models.PositiveSmallIntegerField()
    tags = models.ManyToManyField(Tag)
    comment = models.TextField(blank=True)
    resy_auth = models.ForeignKey(ResyAuth, on_delete=models.CASCADE)
    report_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(ReportUser, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"{self.guest} - {self.ratings}"



class ResyRatingSummary(models.Model):
    month = models.CharField(max_length=20)
    rating = models.DecimalField(max_digits=3, decimal_places=2)
    three_or_below = models.CharField(max_length=10, blank=True)
    total_ratings = models.PositiveIntegerField()
    avg_rating_all_time = models.DecimalField(max_digits=3, decimal_places=2)
    three_or_below_all_time = models.PositiveIntegerField()
    total_ratings_all_time = models.PositiveIntegerField()
    resy_auth = models.ForeignKey(ResyAuth, on_delete=models.CASCADE)
    report_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Summary for {self.month}"
