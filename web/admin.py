from django.contrib import admin
from django.shortcuts import render
from django.urls import path
from web.forms import NotificationForm
from web.models import UnitFile
from web.models.category import Category
from web.models.document import Document
from web.models.queue_email import QueueEmail
from web.models.quickbooks import QuickBooksCredentials, QBReportJson
from web.models.quickbooks import QuickBooksCredentials, QBReportJson
from web.models import (
    User,
    Unit,
    Group,
    Task,
    Assistant,
    Brand,
    BrandOwner,
    Meeting,
    BlockCategory,
    FileBlock,
    LLMChat,
    URLBlock,
    UserBrand,
    ToastSalesSummaryReport,
    Reservation,
    Notification,
    Customer,
    Event,
    OTP,
    OpenAIFile,
    FirebaseCloudMessaging,
    MeetingQuiz,
    ExportModel,
    Category,
)
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.html import format_html

from web.utils import PushNotification

admin.site.register(QBReportJson)
admin.site.register(UnitFile)
admin.site.register(Assistant)

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner','email')

@admin.register(BrandOwner)
class BrandOwnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')

admin.site.register(FileBlock)
admin.site.register(URLBlock)
admin.site.register(UserBrand)
admin.site.register(Notification)
admin.site.register(Customer)
admin.site.register(Event)
admin.site.register(OpenAIFile)
admin.site.register(OTP)
admin.site.register(MeetingQuiz)
admin.site.register(QueueEmail)
admin.site.register(Document)


@admin.register(BlockCategory)
class BlockCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "description")


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "type", "is_enabled", "parent")


class ExportModelAdmin(admin.ModelAdmin):
    list_display = ("title", "is_enabled", "parent","type")


admin.site.register(Category, CategoryAdmin)
admin.site.register(ExportModel, ExportModelAdmin)


class BaseAdmin(admin.ModelAdmin):
    ordering = ("-updated_at",)
    list_display = ("__str__", "updated_at")


@admin.register(LLMChat)
class LLMChatAdmin(admin.ModelAdmin):
    ordering = ("-updated_at",)
    search_fields = ["messages__key"]


@admin.register(ToastSalesSummaryReport)
class ToastSalesSummaryReportAdmin(BaseAdmin):
    pass


class TaskInline(admin.TabularInline):
    model = Task
    extra = 0
    fields = (
        "created_by",
        "assignee",
        "status",
        "created_at",
        "description",
        "unit",
        "due_date",
    )
    readonly_fields = ("created_at",)


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    inlines = [TaskInline]
    list_display = ("id", "name", "created_at", "unit", "created_by","file_id")
    search_fields = ("created_at", "name")
    list_filter = ('created_at', 'created_by')



@admin.register(Reservation)
class ReservationAdmin(BaseAdmin):
    pass


class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class MyUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    model = User
    list_display = (
        "username",
        "display_units",
        "display_brands",
        "role",
        "affiliation",
    )
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            None,
            {
                "fields": (
                    "phone_number",
                    "role",
                    "email_signature",
                    "rate",
                    "paytype",
                    "unit",
                    "units",
                    "affiliation",
                    "xmeeting_minutes", 
                    "stk_minutes",
                    "tokens"
                )
            },
        ),
        (
            "Units and Brands",
            {"fields": ("display_units_field", "display_brands_field")},
        ),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            None,
            { 
                "fields": (
                    "first_name",
                    "last_name",
                    "phone_number",
                    "email_signature",
                    "rate",
                    "paytype",
                    "unit",
                    "units",
                    "affiliation",
                )
            },
        ),
    )
    readonly_fields = ("display_units_field", "display_brands_field")

    def display_units(self, obj):
        """Method to display a summary or count of units associated with the user in list view."""
        return obj.units.count()  # Or any other string representation you prefer

    display_units.short_description = "Units"

    def display_brands(self, obj):
        """Method to display a summary or count of brands associated with the user in list view."""
        return ",".join([brand.name for brand in obj.brands])

    display_brands.short_description = "Brands"

    def display_units_field(self, obj):
        """Custom field representation for detail view."""
        units = obj.units.all()
        return format_html("<br>".join([unit.name for unit in units]))

    display_units_field.short_description = "Units associated"

    def display_brands_field(self, obj):
        """Custom field representation for detail view."""
        brands = obj.brands.all()
        return format_html("<br>".join([brand.name for brand in brands]))

    display_brands_field.short_description = "Brands associated"


class QuickBooksCredentialsAdmin(admin.ModelAdmin):
    list_display = ("id", "unit", "last_success_at", "created_at", "updated_at")


admin.site.register(QuickBooksCredentials, QuickBooksCredentialsAdmin)


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "description",
        "created_by",
        "assignee",
        "status",
        "created_at",
        "meeting",
        "unit",
        "due_date",
    )
    list_filter = ("status", "created_at", "unit")
    search_fields = ("description",)


@admin.register(FirebaseCloudMessaging)
class FirebaseCloudMessagingAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    list_display = ("user", "shortened_token", "created_at", "updated_at")
    list_display_links = ("user", "shortened_token", "created_at", "updated_at")
    actions = ["send_push_notification"]

    def shortened_token(self, obj):
        token = obj.token
        if len(token) > 20:
            return f"{token[:10]}...{token[-10:]}"
        return token

    shortened_token.short_description = "Token"

    def send_push_notification(self, request, queryset=None):
        """
        Custom admin action to send push notifications.
        """
        print(queryset)
        if "apply" in request.POST:
            form = NotificationForm(request.POST)
            if form.is_valid():
                title = form.cleaned_data["title"]
                body = form.cleaned_data["body"]
                data = form.cleaned_data.get("data")
                send_to_all = form.cleaned_data["send_to_all"]

                push_notification = PushNotification()

                if send_to_all:
                    responses = push_notification.send_notification_to_all_users(
                        title, body, data
                    )
                else:
                    users = form.cleaned_data["users"]
                    user_ids = users.values_list("id", flat=True)
                    responses = push_notification.send_notification_to_specific_users(
                        user_ids, title, body, data
                    )

                # Pass responses to the template for rendering
                return render(
                    request,
                    "admin/send_notification.html",
                    {
                        "form": form,
                        "title": "Send Push Notification",
                        "responses": responses,  # Pass the responses to the template
                    },
                )

        else:

            if queryset is None:
                form = NotificationForm(initial={"users": []})
            else:
                # Extract selected user IDs from the request
                user_ids = queryset.values_list("user_id", flat=True).distinct()
                selected_users = User.objects.filter(id__in=user_ids)

                # Initialize the form with the selected users
                form = NotificationForm(initial={"users": selected_users})

        return render(
            request,
            "admin/send_notification.html",
            {"form": form, "title": "Send Push Notification"},
        )

    send_push_notification.short_description = "Send Push Notification to Users"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "announcement/",
                self.admin_site.admin_view(self.send_push_notification),
                name="send_notification",
            ),
        ]
        return custom_urls + urls
