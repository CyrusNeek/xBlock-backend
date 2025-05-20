import pandas as pd
from datetime import datetime
from report.models.report_user import ReportUser
from report.models.resy_reservation import ResyReservation
from report.models.tag import Tag
from report.models.tock_auth import TockAuth
from report.models.tock_booking import TockBooking
from report.tasks.periodic.toast.crawler import parse_date
from report.tasks.periodic.tock_crawler import is_safe_value, safe_float
from django.db.utils import IntegrityError
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware

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
            record["Status"], TockBooking.BookStatus.AVAILABLE.value
        )

        if record["Status"] == "Available":
            continue  # Skip this record if a duplicate exists

        # report_user = ReportUser.objects.create_safe(
        #     email=email,
        #     phone=phone,
        #     brand=tock.unit.brand,
        #     first_name=first_name,
        #     last_name=last_name,
        # )

        guest_tags = []
        visit_tags = []

        if record["Guest Tags"] and pd.notnull(record["Guest Tags"]):
            tag = record["Guest Tags"]

            if type(record["Guest Tags"]) == float:
                guest_tags.append(
                    Tag.objects.get_or_create(
                        name=str(tag), defaults={"user": tock})[0]
                )

            else:
                for tag in record["Guest Tags"].split(","):
                    guest_tags.append(
                        Tag.objects.get_or_create(
                            name=tag.strip(), defaults={"user": tock}
                        )[0]
                    )

        if record["Visit Tags"] and pd.notnull(record["Visit Tags"]):
            tag = record["Visit Tags"]

            if type(record["Visit Tags"]) == float:
                visit_tags.append(
                    Tag.objects.get_or_create(
                        name=str(tag), defaults={"user": tock})[0]
                )

            else:
                for tag in record["Visit Tags"].split(","):
                    visit_tags.append(
                        Tag.objects.get_or_create(
                            name=tag.strip(), defaults={"user": tock}
                        )[0]
                    )

        # visit_tags = [Tag.objects.get_or_create(name=tag.strip())[0] for tag in record['Visit Tags'].split(',')] if record['Visit Tags'] else []

        booking = TockBooking.objects.filter(
            confirmation=record["Confirmation"]).first()

        if booking is None:
            booking = TockBooking()

        booking.tock = tock
        booking.report_triggered_at = datetime.now()
        booking.time = time_obj
        booking.status = status
        booking.postal_code = record["Postal Code"]
        booking.booking_owner = record["Booking Owner"]
        # booking.user = report_user
        booking.email = email,
        booking.phone = phone,
        booking.brand = tock.unit.brand,
        booking.first_name = first_name,
        booking.last_name = last_name,
        booking.experience = record["Experience"]
        booking.price_per_person = safe_float(record["Price Per Person"])
        booking.supplements = record["Supplements"]
        booking.question_answers = record["Question Answers"]
        booking.visit_notes = record["Visit notes"]
        booking.visit_dietary_notes = record["Visit dietary notes"]
        booking.guest_provided_order_notes = record["Guest-provided order notes"]
        booking.guest_notes = record["Guest notes"]
        booking.dietary_notes = record["Dietary notes"]
        booking.total_price = safe_float(record["Total Price"])
        booking.gross_amount_paid = safe_float(record["Gross amount paid"])
        booking.net_amount_paid = safe_float(record["Net amount paid"])
        booking.service_charge = safe_float(record["Service Charge"])
        booking.gratuity = safe_float(record["Gratuity"])
        booking.confirmation = record["Confirmation"]
        booking.visits = safe_float(record["Visits"])
        booking.last_visit_date = (
            parse_date(record["Last Visit Date"], "%Y-%m-%d")
            if record["Last Visit Date"]
            else None
        )
        booking.last_visit_time = (
            parse_date(record["Last Visit Time"], "%I:%M %p").time()
            if is_safe_value(record["Last Visit Time"])
            else None
        )
        booking.group_visits = (
            int(record["Group Visits"]) if pd.notnull(
                record["Group Visits"]) else 0
        )
        booking.last_group_visit_date = (
            parse_date(record["Last Group Visit Date"], "%Y-%m-%d")
            if record["Last Group Visit Date"]
            else None
        )
        booking.last_group_visit_time = (
            parse_date(record["Last Group Visit Time"], "%I:%M %p").time()
            if is_safe_value(record["Last Group Visit Time"])
            else None
        )
        booking.last_group_visit_restaurant = record["Last Group Visit Restaurant"]
        booking.spouse_name = record["Spouse Name"]
        booking.birthday = (
            parse_date(record["Birthday"], "%Y-%m-%d")
            if record["Birthday"]
            else None
        )
        booking.booking_method = record["Booking Method"]
        booking.modified_by = record["Modified By"]
        booking.final_status = record["Final Status"]
        booking.tables = (
            record["Tables"].replace(" ", "")
            if pd.notnull(record["Tables"]) and type(record['Tables']) != int
            else str(record['Tables']) if type(record['Tables']) == int else ""
        )
        booking.servers = record["Servers"]
        booking.dining_time_seconds = (
            safe_float(record["Dining Time (seconds)"])
            if record["Dining Time (seconds)"]
            else 0
        )

        records_to_create.append(booking)

        try:
            booking.save()

            # Adding ManyToMany relationships after saving the instance
            for tag in guest_tags:
                booking.guest_tags.add(tag)
            for tag in visit_tags:
                booking.visit_tags.add(tag)
        except IntegrityError:
            pass

    return len(records_to_create)


def save_resy_bookings(transactions, resy, reservation_date):
    """
    Save the Resy bookings from the CSV file to the database.
    
    Args:
        transactions: List of dicts representing CSV rows
        tock: The TockAuth instance related to the bookings
        reservation_date: Date extracted from the file name in YYYY-MM-DD format
    
    Returns:
        int: The number of records successfully saved
    """
    reservations_to_create = []

    for row in transactions:
        try:
            reservation_time = row['Time']  # This is in '12:00:00' format
            party_size = row.get('Party_Size', None)
            phone = row.get('phone', '')
            email = row.get('Email', None)
            guest_name = row.get('Guest', '')
            service = row.get('service', '')
            status = row.get('status', '')
            table = row.get('table', None)
            visit_note = row.get('Visit_Note', '')
            reserve_number = row.get('Reservation_id', '')

            # Combine the extracted date with time from CSV to create a full datetime
            datetime_str = f"{reservation_date} {reservation_time}"
            datetime_obj = make_aware(parse_datetime(datetime_str))

            # Prepare the reservation object
            reservation = ResyReservation(
                resy_auth=resy,
                time=reservation_time,
                reservation_date=reservation_date,
                service=service,
                guest=guest_name,
                phone=phone,
                email=email,
                party_size=party_size,
                status=status,
                table=table,
                visit_note=visit_note,
                reserve_number=reserve_number,
                datetime=datetime_obj,
                is_new=True,  # Mark as new
                first_name='',  # Extract if needed from guest_name
                last_name='',   # Extract if needed from guest_name
            )

            reservations_to_create.append(reservation)

        except Exception as e:
            print(f"Error processing row: {row}, Error: {e}")
            continue

    # Bulk create to improve performance
    ResyReservation.objects.bulk_create(reservations_to_create, ignore_conflicts=True)

    return len(reservations_to_create)