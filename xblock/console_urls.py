"""
URL configuration for the admin console.
This is used when CONSOLE_MODE is enabled to restrict the site to admin functionality only.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='admin:index')),  # Redirect root to admin
]
