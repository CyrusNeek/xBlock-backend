from django.contrib import admin
from .models import Role, PermissionCategory, Permission

@admin.register(Role)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ["label", "brand_owner", "is_active", "creator", "is_superuser", "key_code"]

@admin.register(PermissionCategory)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ["label", "is_active", "group_type"]
    list_filter = ["group_type"]

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ["label", "is_active", "category", "component_key"]
    list_filter = ["category"]
    search_fields = ["label__istartswith"]