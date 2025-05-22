import csv
import datetime
import re
from tempfile import NamedTemporaryFile
from django.contrib import admin

from report.models.guest_profile import Guest, GuestProfile

from .helpers import save_resy_bookings, save_tock_bookings

from .models import (
    TockAuth,
    TockBooking,
    Event,
    ReportUser,
    Tag,
    ToastCheckDetails,
    SSHKey,
    ToastItemSelectionDetails,
    ToastModifiersSelectionDetails,
    ToastOrder,
    ToastTimeEntries,
    ToastAuth,
    ToastCashTransaction,
    ToastPayment,
    ResyAuth,
    ResyRating,
    ResyRatingSummary,
    ResyReservation,
    AnalyticReport,
)
from django.urls import path
from django.shortcuts import render, redirect


@admin.register(AnalyticReport)
class AnalyticReportAdmin(admin.ModelAdmin):
    list_display = [
        "model_name",
        "datetime",
        "status",
        "unit",
        "created_at",
    ]


@admin.register(ReportUser)
class ReportUserAdmin(admin.ModelAdmin):
    list_display = ["full_name"]
    list_filter = ["brand", "uploaded"]


admin.site.register(TockAuth)
admin.site.register(ToastAuth)
admin.site.register(Event)
admin.site.register(ToastCashTransaction)
admin.site.register(Tag)
admin.site.register(ToastCheckDetails)
admin.site.register(SSHKey)
admin.site.register(ToastItemSelectionDetails)
admin.site.register(ToastModifiersSelectionDetails)
admin.site.register(ToastTimeEntries)
admin.site.register(ToastPayment)
admin.site.register(ResyAuth)
admin.site.register(ResyRating)
admin.site.register(ResyRatingSummary)
admin.site.register(Guest)


@admin.register(GuestProfile)
class GuestProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "model_name",
        "reservation_date",
        "unit",
        "total_price",
        "matched",
        "uploaded",
        "created_at",
        "updated_at",
    ]
    list_filter = ["model_name", "matched", "uploaded", "reservation_date", "unit"]
    search_fields = ["user__first_name", "user__last_name", "model_name", "tables"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "reservation_date"
    ordering = ["-created_at"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("user", "unit")


@admin.register(ResyReservation)
class ResyReservationAdmin(admin.ModelAdmin):
    change_list_template = "admin/resy_document_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "upload/",
                self.admin_site.admin_view(self.upload_file),
                name="document-upload-resy",
            ),
        ]
        return custom_urls + urls

    def extract_date_from_filename(self, filename):
        """
        Extracts the reservation date from the given filename using regex.
        Expected format: degidios_restaurant_reservation_report_Fri._Dec_03,_2021
        Returns the date string in the format 'YYYY-MM-DD'.
        """
        match = re.search(r"[A-Za-z]+\._([A-Za-z]+)_(\d{2}),_(\d{4})", filename)
        if match:
            month = match.group(1)
            day = match.group(2)
            year = match.group(3)
            date_str = f"{month} {day}, {year}"
            date_obj = datetime.datetime.strptime(date_str, "%b %d, %Y")
            return date_obj.strftime("%Y-%m-%d")  # Format as YYYY-MM-DD
        return None

    def upload_file(self, request):
        if request.method == "POST":
            # Handle multiple file uploads
            files = request.FILES.getlist("file")
            resy_id = request.POST["tock"]
            resy = ResyAuth.objects.get(pk=resy_id)

            # Process each uploaded file
            total_records = 0
            for file in files:
                file_name = file.name
                reservation_date = self.extract_date_from_filename(
                    file_name
                )  # Extract date from filename

                if not reservation_date:
                    print(f"Could not extract date from filename: {file_name}")
                    continue

                with NamedTemporaryFile(delete=False) as temp_file:
                    for chunk in file.chunks():
                        temp_file.write(chunk)
                    temp_file_path = temp_file.name

                # Read the CSV file
                with open(temp_file_path, newline="") as csvfile:
                    reader = csv.DictReader(csvfile)
                    transactions = [row for row in reader]

                # Save the bookings using the extracted date
                number_of_records = save_resy_bookings(
                    transactions, resy, reservation_date
                )
                total_records += number_of_records

            print(
                f"Successfully imported {total_records} bookings from {len(files)} files"
            )
            return redirect("admin:report_resyreservation_changelist")

        resy = ResyAuth.objects.all().values("unit__brand__name", "unit__name", "pk")
        return render(request, "admin/upload_toast.html", {"resy": resy})

    list_display = (
        "reserve_number",
        "guest",
        "party_size",
        "status",
        "datetime",
        "table",
        "service",
        "phone",
        "email",
        "created_at",
        "updated_at",
        "uploaded",
    )

    search_fields = (
        "guest",
        "phone",
        "email",
        "status",
        "reserve_number",
        "table",
        "service",
    )

    list_filter = (
        "status",
        "service",
        "datetime",
        "uploaded",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Reservation Details",
            {
                "fields": (
                    "resy_auth",
                    "guest",
                    "phone",
                    "email",
                    "party_size",
                    "status",
                    "service",
                    "first_name",
                    "last_name",
                    "brand",
                )
            },
        ),
        (
            "Timing Information",
            {"fields": ("time", "reservation_date", "datetime", "table")},
        ),
        ("Notes", {"fields": ("visit_note",)}),
        ("Other Information", {"fields": ("reserve_number", "uploaded")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at", "datetime")
    ordering = ("-datetime",)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ("reserve_number", "resy_auth")
        return self.readonly_fields


@admin.register(TockBooking)
class TockBookingAdmin(admin.ModelAdmin):
    change_list_template = "admin/document_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "upload/",
                self.admin_site.admin_view(self.upload_file),
                name="document-upload",
            ),
        ]
        return custom_urls + urls

    def upload_file(self, request):
        if request.method == "POST":
            file = request.FILES["file"]
            tock_id = request.POST["tock"]
            tock = TockAuth.objects.get(pk=tock_id)
            with NamedTemporaryFile(delete=False) as temp_file:
                for chunk in file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name

            # Read the CSV file
            with open(temp_file_path, newline="") as csvfile:
                reader = csv.DictReader(csvfile)
                transactions = [row for row in reader]

            # Save the bookings
            number_of_records = save_tock_bookings(transactions, tock)
            print(f"Successfully imported {number_of_records} bookings")
            return redirect("admin:report_tockbooking_changelist")

        tocks = TockAuth.objects.all().values("unit__brand__name", "unit__name", "pk")
        return render(request, "admin/upload_tock.html", {"tocks": tocks})

    list_display = (
        "user",
        "time",
        "status",
        "party_size",
        "booking_owner",
        "total_price",
        "gross_amount_paid",
        "net_amount_paid",
        "last_visit_date",
        "confirmation",
        "visits",
        "group_visits",
    )

    search_fields = ("booking_owner",)

    # Fields to filter by
    list_filter = (
        "status",
        "time",
        "party_size",
        "last_visit_date",
        "last_group_visit_date",
        "booking_method",
        "uploaded",
    )

    # Fieldsets to organize fields in the detail view
    fieldsets = (
        (
            "Booking Details",
            {
                "fields": (
                    "user",
                    "tock",
                    "time",
                    "status",
                    "party_size",
                    "booking_owner",
                )
            },
        ),
        (
            "Pricing",
            {
                "fields": (
                    "price_per_person",
                    "total_price",
                    "gross_amount_paid",
                    "net_amount_paid",
                    "service_charge",
                    "gratuity",
                )
            },
        ),
        (
            "Notes and Tags",
            {
                "fields": (
                    "tags",
                    "guest_tags",
                    "visit_tags",
                    "question_answers",
                    "visit_notes",
                    "visit_dietary_notes",
                    "guest_provided_order_notes",
                    "guest_notes",
                    "dietary_notes",
                )
            },
        ),
        (
            "Visit Information",
            {
                "fields": (
                    "visits",
                    "last_visit_date",
                    "last_visit_time",
                    "group_visits",
                    "last_group_visit_date",
                    "last_group_visit_time",
                    "last_group_visit_restaurant",
                )
            },
        ),
        (
            "Additional Information",
            {
                "fields": (
                    "birthday",
                    "spouse_name",
                    "booking_method",
                    "modified_by",
                    "final_status",
                    "tables",
                    "servers",
                    "dining_time_seconds",
                    "uploaded",
                    "confirmation",
                )
            },
        ),
    )

    prepopulated_fields = {}
    readonly_fields = ("report_triggered_at",)
    filter_horizontal = ("tags", "guest_tags", "visit_tags")
    date_hierarchy = "time"
    ordering = ("-time",)


@admin.register(ToastOrder)
class ToastOrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_id",
        "order_number",
        "user",
        "is_valid",
        "opened",
        "server",
        "table",
        "amount",
        "total",
        "paid",
        "closed",
        "voided",
        "uploaded",
    )

    search_fields = (
        "order_id",
        "order_number",
        "server",
        "table",
        "revenue_center",
        "dining_area",
    )

    list_filter = (
        "is_valid",
        "voided",
        "opened",
        "paid",
        "closed",
        "order_source",
        "uploaded",
        "table",
    )

    fieldsets = (
        (
            "Order Information",
            {
                "fields": (
                    "order_id",
                    "order_number",
                    "user",
                    "toast_auth",
                    "is_valid",
                    "uploaded",
                )
            },
        ),
        ("Timing", {"fields": ("opened", "paid", "closed", "duration_opened_to_paid")}),
        (
            "Details",
            {
                "fields": (
                    "checks",
                    "number_of_guests",
                    "tab_names",
                    "server",
                    "table",
                    "revenue_center",
                    "dining_area",
                    "service",
                    "dining_options",
                    "order_source",
                )
            },
        ),
        (
            "Financial Information",
            {
                "fields": (
                    "discount_amount",
                    "amount",
                    "tax",
                    "tip",
                    "gratuity",
                    "total",
                    "voided",
                )
            },
        ),
    )

    readonly_fields = ("duration_opened_to_paid", "order_number")
    date_hierarchy = "opened"
    ordering = ("-opened",)
    actions = ["mark_as_valid", "mark_as_invalid"]

    def mark_as_valid(self, request, queryset):
        queryset.update(is_valid=True)

    mark_as_valid.short_description = "Mark selected orders as valid"

    def mark_as_invalid(self, request, queryset):
        queryset.update(is_valid=False)

    mark_as_invalid.short_description = "Mark selected orders as invalid"
