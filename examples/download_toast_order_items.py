from report.tasks.periodic.toast.crawler import ToastCrawler
from report.models import *
from report.tasks.periodic.toast.item_selection_details_crawl import *


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
        file_name="ItemSelectionDetails.csv",
    ).get_data()

    df = result["result"]

    transactions = df.to_dict(orient="records")

    transaction_instances = []

    for transaction in transactions:
        try:
            sent_date = datetime.strptime(transaction["Sent Date"], input_format)
            order_date = datetime.strptime(transaction["Order Date"], input_format)

            order = ToastOrder.objects.get(order_id=safe_id(transaction["Order Id"]))

            transaction_instances.append(
                ToastItemSelectionDetails(
                    toast=toast,
                    order=order,
                    sent_date=sent_date,
                    order_date=order_date,
                    check_id=transaction["Check Id"],
                    server=transaction.get("Server", ""),
                    table=transaction.get("Table", ""),
                    dining_area=transaction.get("Dining Area", ""),
                    service=transaction.get("Service", ""),
                    dining_option=transaction.get("Dining Option", ""),
                    item_selection_id=transaction["Item Selection Id"],
                    item_id=transaction["Item Id"],
                    master_id=transaction["Master Id"],
                    sku=transaction.get("SKU", ""),
                    plu=transaction.get("PLU", ""),
                    menu_item=transaction.get("Menu Item", ""),
                    menu_subgroups=transaction.get("Menu Subgroup(s)", ""),
                    menu_group=transaction.get("Menu Group", ""),
                    menu=transaction.get("Menu", ""),
                    sales_category=transaction.get("Sales Category", ""),
                    gross_price=round(transaction["Gross Price"], 2),
                    discount=round(transaction["Discount"], 2),
                    net_price=round(transaction["Net Price"], 2),
                    quantity=round(transaction["Qty"], 2),
                    tax=round(transaction["Tax"], 2),
                    void=transaction["Void?"],
                    deferred=transaction["Deferred"],
                    tax_exempt=transaction["Tax Exempt"],
                    tax_inclusion_option=transaction.get("Tax Inclusion Option", ""),
                    dining_option_tax=transaction.get("Dining Option Tax", ""),
                    tab_name=transaction.get("Tab Name", ""),
                )
            )
        except Exception as e:
            print(f"Error processing transaction: {transaction}")
            raise e

    ToastItemSelectionDetails.objects.bulk_create(
        transaction_instances, ignore_conflicts=True
    )


if __name__ == "django.core.management.commands.shell":
    main()
