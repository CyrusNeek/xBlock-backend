from report.models import *

from report.tasks.periodic.toast.item_selection_details_crawl import *

import pandas as pd


name = "OrderDetails_2023_01_01-2023_02_28.csv"

def main():
    toast = ToastAuth.objects.get(id=2)
    
    cols = pd.read_csv(
        open(name, "r"), nrows=1
    ).columns
        
    df = pd.read_csv(open(name, "r"), usecols=cols)

    transactions = df.to_dict(orient="records")

    transactions = df.to_dict(orient="records")

    transaction_instances = []

    for transaction in transactions:
        opened_date = datetime.strptime(transaction["Opened"], input_format)
        paid_date = (
            datetime.strptime(transaction["Paid"], input_format)
            if pd.notnull(transaction["Paid"])
            else None
        )
        closed_date = (
            datetime.strptime(transaction["Closed"], input_format)
            if pd.notnull(transaction["Closed"])
            else None
        )

        transaction_instances.append(
            ToastOrder(
                toast_auth=toast,
                order_id=transaction["Order Id"],
                order_number=int(transaction["Order #"]),
                checks=int(transaction["Checks"].split(", ")[0]) if type(transaction["Checks"]) != int else int(transaction["Checks"]),
                opened=opened_date,
                number_of_guests=int(transaction["# of Guests"].split(", ")[0]) if type(transaction["# of Guests"]) != int else int(transaction["# of Guests"]),
                tab_names=(
                    transaction["Tab Names"]
                    if pd.notnull(transaction["Tab Names"])
                    else None
                ),
                server=(
                    transaction["Server"] if pd.notnull(transaction["Server"]) else None
                ),
                table=(
                    transaction["Table"] if pd.notnull(transaction["Table"]) else None
                ),
                revenue_center=(
                    transaction["Revenue Center"]
                    if pd.notnull(transaction["Revenue Center"])
                    else None
                ),
                dining_area=(
                    transaction["Dining Area"]
                    if pd.notnull(transaction["Dining Area"])
                    else None
                ),
                service=(
                    transaction["Service"]
                    if pd.notnull(transaction["Service"])
                    else None
                ),
                dining_options=(
                    transaction["Dining Options"]
                    if pd.notnull(transaction["Dining Options"])
                    else None
                ),
                discount_amount=(
                    float(transaction["Discount Amount"])
                    if pd.notnull(transaction["Discount Amount"])
                    else None
                ),
                amount=(
                    float(transaction["Amount"])
                    if pd.notnull(transaction["Amount"])
                    else None
                ),
                tax=(
                    float(transaction["Tax"])
                    if pd.notnull(transaction["Tax"])
                    else None
                ),
                tip=(
                    float(transaction["Tip"])
                    if pd.notnull(transaction["Tip"])
                    else None
                ),
                gratuity=(
                    float(transaction["Gratuity"])
                    if pd.notnull(transaction["Gratuity"])
                    else None
                ),
                total=(
                    float(transaction["Total"])
                    if pd.notnull(transaction["Total"])
                    else None
                ),
                voided=(
                    bool(transaction["Voided"])
                    if pd.notnull(transaction["Voided"])
                    else False
                ),
                paid=paid_date,
                closed=closed_date,
                duration_opened_to_paid=(
                    transaction["Duration (Opened to Paid)"]
                    if pd.notnull(transaction["Duration (Opened to Paid)"])
                    else None
                ),
                order_source=(
                    transaction["Order Source"]
                    if pd.notnull(transaction["Order Source"])
                    else None
                ),
            )
        )

    ToastOrder.objects.bulk_create(transaction_instances)





if __name__ == "django.core.management.commands.shell":
    main()
