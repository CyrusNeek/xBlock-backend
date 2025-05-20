import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from report.models import TockAuth
from report.models import TockBooking, ReportUser, Tag  # Adjust accordingly
from report.tasks.periodic.tock_crawler import safe_float, parse_date, is_safe_value
import pandas as pd


def save_tock_bookings(transactions, tock: TockAuth):
    records_to_create = []
    for record in transactions:
        date_str = record["Date"]
        time_str = record["Time"]
        datetime_str = f"{date_str} {time_str}"

        try:
            time_obj = datetime.strptime(datetime_str, "%Y-%m-%d %I:%M %p")
        except Exception:
            time_obj = None

        email = record.get("Email")
        phone = record.get("Phone")
        first_name = record.get("First Name")
        last_name = record.get("Last Name")

        status_map = {
            "Available": TockBooking.BookStatus.AVAILABLE.value,
            "Canceled": TockBooking.BookStatus.CANCELED.value,
            "Booked": TockBooking.BookStatus.BOOKED.value,
        }

        status = status_map.get(
            record["Status"], TockBooking.BookStatus.AVAILABLE.value)

        try:
            report_user, created = ReportUser.objects.get_or_create(
                email=email,
                phone=phone,
                brand=tock.unit.brand,
                defaults={'first_name': first_name, 'last_name': last_name},
            )
        except Exception as e:
            print(f"Error creating or getting ReportUser: {e}")
            continue

        guest_tags = []
        visit_tags = []

        if record["Guest Tags"] and pd.notnull(record["Guest Tags"]):
            tag = record["Guest Tags"]

            if isinstance(record["Guest Tags"], float):
                guest_tags.append(Tag.objects.get_or_create(
                    name=str(tag), defaults={"user": tock})[0])
            else:
                for tag in record["Guest Tags"].split(","):
                    guest_tags.append(Tag.objects.get_or_create(
                        name=tag.strip(), defaults={"user": tock})[0])

        if record["Visit Tags"] and pd.notnull(record["Visit Tags"]):
            tag = record["Visit Tags"]

            if isinstance(record["Visit Tags"], float):
                visit_tags.append(Tag.objects.get_or_create(
                    name=str(tag), defaults={"user": tock})[0])
            else:
                for tag in record["Visit Tags"].split(","):
                    visit_tags.append(Tag.objects.get_or_create(
                        name=tag.strip(), defaults={"user": tock})[0])

        booking = TockBooking(
            tock=tock,
            report_triggered_at=datetime.now(),
            time=time_obj,
            status=status,
            postal_code=record["Postal Code"],
            party_size=int(record["Party Size"]),
            booking_owner=record["Booking Owner"],
            # user=report_user,
            email=email,
            phone=phone,
            brand=tock.unit.brand,
            first_name=first_name,
            last_name=last_name,
            experience=record["Experience"],
            price_per_person=safe_float(record["Price Per Person"]),
            supplements=record["Supplements"],
            question_answers=record["Question Answers"],
            visit_notes=record["Visit notes"],
            visit_dietary_notes=record["Visit dietary notes"],
            guest_provided_order_notes=record["Guest-provided order notes"],
            guest_notes=record["Guest notes"],
            dietary_notes=record["Dietary notes"],
            total_price=safe_float(record["Total Price"]),
            gross_amount_paid=safe_float(record["Gross amount paid"]),
            net_amount_paid=safe_float(record["Net amount paid"]),
            service_charge=safe_float(record["Service Charge"]),
            gratuity=safe_float(record["Gratuity"]),
            confirmation=record["Confirmation"],
            visits=safe_float(record["Visits"]),
            last_visit_date=(
                parse_date(record["Last Visit Date"],
                           "%Y-%m-%d") if record["Last Visit Date"] else None
            ),
            last_visit_time=(
                parse_date(record["Last Visit Time"], "%I:%M %p").time(
                ) if is_safe_value(record["Last Visit Time"]) else None
            ),
            group_visits=int(record["Group Visits"]) if pd.notnull(
                record["Group Visits"]) else 0,
            last_group_visit_date=(
                parse_date(record["Last Group Visit Date"],
                           "%Y-%m-%d") if record["Last Group Visit Date"] else None
            ),
            last_group_visit_time=(
                parse_date(record["Last Group Visit Time"], "%I:%M %p").time(
                ) if is_safe_value(record["Last Group Visit Time"]) else None
            ),
            last_group_visit_restaurant=record["Last Group Visit Restaurant"],
            spouse_name=record["Spouse Name"],
            birthday=(
                parse_date(record["Birthday"],
                           "%Y-%m-%d") if record["Birthday"] else None
            ),
            booking_method=record["Booking Method"],
            modified_by=record["Modified By"],
            final_status=record["Final Status"],
            tables=record["Tables"].replace(
                " ", "") if pd.notnull(record["Tables"]) else "",
            servers=record["Servers"],
            dining_time_seconds=safe_float(
                record["Dining Time (seconds)"]) if record["Dining Time (seconds)"] else 0,
        )

        records_to_create.append(booking)

        booking.save()

        for tag in guest_tags:
            booking.guest_tags.add(tag)
        for tag in visit_tags:
            booking.visit_tags.add(tag)

    return len(records_to_create)


def main():
    csv_files = [
        'butcher.csv',
    ]
    for csv_file in csv_files:
        with open(csv_file, newline='') as file:
            reader = csv.DictReader(file)
            next(reader, None)  # Skip the header row

            transactions = []
            for row in reader:
                transactions.append(row)

            # Replace with your actual TockAuth instance, this is just a placeholder
            # Butcher and the Boar TockAuth primary key
            tock = TockAuth.objects.get(pk=2)

            # Call your save_tock_bookings function
            number_of_records = save_tock_bookings(transactions, tock)
            print(f'Successfully imported {number_of_records} bookings')


if __name__ == "django.core.management.commands.shell":
    main()
