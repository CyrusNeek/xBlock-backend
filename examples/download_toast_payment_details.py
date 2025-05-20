from report.tasks.periodic.toast.crawler import ToastCrawler
from report.models import *
from report.tasks.periodic.toast.payment_details_crawl import *


def main():

    filename = "tmp-1.pem"

    toast = ToastAuth.objects.first()

    date = "20231021"

    result = ToastCrawler(
        host=toast.host,
        username=toast.username,
        location_id=toast.location_id,
        private_key_path=filename,
        date_time=(date),
        file_name="PaymentDetails.csv",
    ).get_data()

    df = result["result"]

    transactions = df.to_dict(orient="records")

    transaction_instances = []

    for row in transactions:
        paid_date = parse_date(row["Paid Date"])
        order_date = parse_date(row["Order Date"])
        refund_date = (
            parse_date(row["Refund Date"], "%m/%d/%Y %I:%M %p")
            if pd.notnull(row["Refund Date"])
            else None
        )

        void_date = (
            parse_date(row["Void Date"], "%m/%d/%Y %I:%M %p")
            if pd.notnull(row["Void Date"])
            else None
        )

        order = ToastOrder.objects.get(order_id=row["Order Id"])

        report_user, _ = ReportUser.objects.get_or_create(
            email=row["Email"] if row["Email"] else None,
            phone=row["Phone"] if row["Phone"] else None,
            brand=toast.unit.brand,
        )

        transaction_instances.append(
            ToastPayment(
                payment_id=row["Payment Id"],
                order=order,
                paid_date=paid_date,
                order_date=order_date,
                check_id=row["Check Id"],
                check_number=row["Check #"],
                tab_name=row["Tab Name"] if pd.notnull(row["Tab Name"]) else None,
                server=row["Server"] if pd.notnull(row["Server"]) else None,
                table=row["Table"] if pd.notnull(row["Table"]) else None,
                dining_area=(
                    row["Dining Area"] if pd.notnull(row["Dining Area"]) else None
                ),
                service=row["Service"] if pd.notnull(row["Service"]) else None,
                dining_option=(
                    row["Dining Option"] if pd.notnull(row["Dining Option"]) else None
                ),
                house_account=(
                    row["House Acct #"] if pd.notnull(row["House Acct #"]) else None
                ),
                amount=safe_float(row["Amount"]),
                tip=safe_float(row["Tip"]),
                gratuity=safe_float(row["Gratuity"]),
                total=safe_float(row["Total"]),
                swiped_card_amount=safe_float(row["Swiped Card Amount"]),
                keyed_card_amount=safe_float(row["Keyed Card Amount"]),
                amount_tendered=safe_float(row["Amount Tendered"]),
                refunded=row["Refunded"] if pd.notnull(row["Refunded"]) else None,
                refund_date=refund_date,
                refund_amount=safe_float(row["Refund Amount"]),
                refund_tip_amount=safe_float(row["Refund Tip Amount"]),
                void_user=row["Void User"] if pd.notnull(row["Void User"]) else None,
                void_approver=(
                    row["Void Approver"] if pd.notnull(row["Void Approver"]) else None
                ),
                void_date=void_date,
                status=row["Status"],
                type=row["Type"],
                cash_drawer=(
                    row["Cash Drawer"] if pd.notnull(row["Cash Drawer"]) else None
                ),
                card_type=row["Card Type"] if pd.notnull(row["Card Type"]) else None,
                other_type=row["Other Type"] if pd.notnull(row["Other Type"]) else None,
                user=report_user,
                last_4_card_digits=(
                    row["Last 4 Card Digits"]
                    if pd.notnull(row["Last 4 Card Digits"])
                    else None
                ),
                vmcd_fees=safe_float(row["V/MC/D Fees"]),
                room_info=(
                    row["Room Info"] if pd.notnull(row.get("Room Info")) else None
                ),
                receipt=row["Receipt"] if pd.notnull(row["Receipt"]) else None,
                source=row["Source"],
            )
        )

    ToastPayment.objects.bulk_create(transaction_instances, ignore_conflicts=True)


if __name__ == "django.core.management.commands.shell":
    main()
