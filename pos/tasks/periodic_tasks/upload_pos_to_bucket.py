import logging
from celery import shared_task
from examples.bucket_upload_helper import upload_data_in_bucket
from pos.models import (
    Customer,
    DiscountPromotion,
    Inventory,
    Payment,
    RestaurantLocation,
    ShiftDetail,
    Staff,
    TechnicalMetadata,
    TransactionItem,
    Transaction,
)

logger = logging.getLogger(__name__)


def upload_customer_in_bucket():
    customers = Customer.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in customers:
        data = {
            "customer_id": item.pk,
            "first_name": item.first_name,
            "last_name": item.last_name,
            "email": item.email,
            "phone_number": item.phone_number,
            "loyalty_program_id": (
                item.loyalty_program_id if item.loyalty_program_id else None
            ),
            "loyalty_points": item.loyalty_points if item.loyalty_points else None,
            "birthdate": (
                item.birthdate.strftime("%Y-%m-%d") if item.birthdate else None
            ),
            "gender": item.gender if item.gender else None,
            "preferred_language": (
                item.preferred_language if item.preferred_language else None
            ),
            "marketing_opt_in": item.marketing_opt_in if item.marketing_opt_in else None,
            "customer_tags": (item.customer_tags if item.customer_tags else []),
            "total_visits": item.total_visits if item.total_visits else None,
            "total_spend": item.total_spend if item.total_spend else None,
            "last_visit_date": (
                item.last_visit_date.strftime("%Y-%m-%d")
                if item.last_visit_date
                else None
            ),
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="pos",
                model_name="customer",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading Customer (ID {item.pk}) to GCP: {e}")

    Customer.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_discount_promotion_in_bucket():
    discount_promotions = DiscountPromotion.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in discount_promotions:
        data = {
            "discount_promotion_id": item.pk,
            "transaction_id": item.transaction.pk,
            "discount_type": item.discount_type,
            "discount_value": item.discount_value,
            "discount_code": item.discount_code if item.discount_code else None,
            "description": item.description if item.description else None,
            "applied_to": item.applied_to if item.applied_to else None,
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="pos",
                model_name="discount_promotion",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(
                f"Error uploading DiscountPromotion (ID {item.pk}) to GCP: {e}"
            )

    DiscountPromotion.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_inventory_in_bucket():
    inventories = Inventory.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in inventories:
        data = {
            "inventory_id": item.pk,
            "item_name": item.item_name,
            "item_sku": item.item_sku,
            "item_category": item.item_category,
            "current_stock_level": item.current_stock_level,
            "reorder_level": item.reorder_level,
            "unit_cost": item.unit_cost,
            "supplier_id": (item.supplier_id if item.supplier_id is not None else None),
            "last_restock_date": (
                item.last_restock_date.strftime("%Y-%m-%d")
                if item.last_restock_date
                else None
            ),
            "notes": item.notes if item.notes is not None else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="pos",
                model_name="inventory",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading Inventory (ID {item.pk}) to GCP: {e}")

    Inventory.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_payment_in_bucket():
    payments = Payment.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in payments:
        data = {
            "payment_id": item.pk,
            "transaction_id": item.transaction.pk,
            "payment_method": item.payment_method,
            "amount": item.amount,
            "payment_processor": item.payment_processor,
            "card_type": item.card_type if item.card_type is not None else None,
            "last_four_digits": (
                item.last_four_digits if item.last_four_digits is not None else None
            ),
            "authorization_code": (
                item.authorization_code if item.authorization_code is not None else None
            ),
            "payment_status": item.payment_status,
            "payment_created_at": item.payment_created_at.strftime(
                "%Y-%m-%d %H:%M:%S.%f"
            ),
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="pos",
                model_name="payment",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading Payment (ID {item.pk}) to GCP: {e}")

    Payment.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_restaurant_location_in_bucket():
    restaurant_locations = RestaurantLocation.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in restaurant_locations:
        data = {
            "restaurant_location_id": item.pk,
            "restaurant_name": item.restaurant_name,
            "address": item.address,
            "city": item.city,
            "state": item.state,
            "zip_code": item.zip_code,
            "country": item.country if item.country else None,
            "phone_number": item.phone_number,
            "email": item.email,
            "venue_capacity": item.venue_capacity,
            "opening_date": item.opening_date.strftime("%Y-%m-%d"),
            "notes": item.notes if item.notes is not None else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="pos",
                model_name="restaurant_location",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(
                f"Error uploading RestaurantLocation (ID {item.pk}) to GCP: {e}"
            )

    RestaurantLocation.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_shift_detail_in_bucket():
    shift_details = ShiftDetail.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in shift_details:
        data = {
            "shift_detail_id": item.pk,
            "staff_id": item.staff.pk,
            "restaurant_location_id": item.restaurant.pk,
            "shift_date": item.shift_date.strftime("%Y-%m-%d"),
            "shift_start_time": item.shift_start_time.strftime("%H:%M:%S.%f"),
            "shift_end_time": item.shift_end_time.strftime("%H:%M:%S.%f"),
            "role": item.role,
            "total_sales": str(item.total_sales),
            "tips_earned": str(item.tips_earned),
            "notes": item.notes if item.notes is not None else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="pos",
                model_name="shift_detail",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading ShiftDetail (ID {item.pk}) to GCP: {e}")

    ShiftDetail.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_staff_in_bucket():
    staff = Staff.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in staff:
        data = {
            "staff_id": item.pk,
            "first_name": item.first_name,
            "last_name": item.last_name,
            "role": item.role,
            "email": item.email,
            "phone_number": item.phone_number,
            "employment_start_date": item.employment_start_date.strftime("%Y-%m-%d"),
            "employment_end_date": (
                item.employment_end_date.strftime("%Y-%m-%d")
                if item.employment_end_date
                else None
            ),
            "notes": item.notes if item.notes is not None else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="pos",
                model_name="staff",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading Staff (ID {item.pk}) to GCP: {e}")

    Staff.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_technical_metadata_in_bucket():
    technical_metadata = TechnicalMetadata.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in technical_metadata:
        data = {
            "technical_metadata_id": item.pk,
            "source_system": item.source_system,
            "data_retrieval_created_at": item.data_retrieval_created_at.strftime(
                "%Y-%m-%d %H:%M:%S.%f"
            ),
            "data_sync_status": item.data_sync_status,
            "api_call": item.api_call if item.api_call else None,
            "processing_notes": (
                item.processing_notes if item.processing_notes else None
            ),
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="pos",
                model_name="technical_metadata",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(
                f"Error uploading TechnicalMetadata (ID {item.pk}) to GCP: {e}"
            )

    TechnicalMetadata.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_transaction_item_in_bucket():
    transaction_items = TransactionItem.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in transaction_items:
        data = {
            "transaction_item_id": item.pk,
            "transaction_id": item.transaction.pk,
            "item_name": item.item_name,
            "item_sku": item.item_sku,
            "item_category": item.item_category,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "modifier_details": (
                item.modifier_details if item.modifier_details is not None else None
            ),
            "discount_applied": item.discount_applied,
            "total_item_price": item.total_item_price,
            "item_inventory_id": (
                item.inventory_item.pk if item.inventory_item else None
            ),
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="pos",
                model_name="transaction_item",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading TransactionItem (ID {item.pk}) to GCP: {e}")

    TransactionItem.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_transaction_in_bucket():
    transactions = Transaction.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in transactions:
        data = {
            "transaction_id": item.pk,
            "pos_system": item.pos_system,
            "restaurant_location_id": item.restaurant_location.pk,
            "transaction_date": item.transaction_date.strftime("%Y-%m-%d"),
            "transaction_time": item.transaction_time.strftime("%H:%M:%S.%f"),
            "order_type": item.order_type,
            "order_status": item.order_status,
            "subtotal_amount": item.subtotal_amount,
            "tax_amount": item.tax_amount,
            "tip_amount": item.tip_amount,
            "total_amount": item.total_amount,
            "discount_amount": item.discount_amount,
            "payment_method": item.payment_method if item.payment_method else None,
            "payment_status": item.payment_status if item.payment_status else None,
            "customer_id": item.customer.pk,
            "staff_id": item.staff.pk if item.staff else None,
            "table_number": item.table_number if item.table_number else None,
            "split_payment_details": (
                item.split_payment_details if item.split_payment_details else None
            ),
            "void_reason": item.void_reason if item.void_reason else None,
            "refund_reason": item.refund_reason if item.refund_reason else None,
            "notes": item.notes if item.notes else None,
            "transaction_datetime": item.transaction_datetime.strftime(
                "%Y-%m-%d %H:%M:%S.%f"
            ),
        }
        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="pos",
                model_name="transaction",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading Transaction (ID {item.pk}) to GCP: {e}")

    Transaction.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


@shared_task
def upload_pos_data_to_bucket():

    upload_customer_in_bucket()
    upload_discount_promotion_in_bucket()
    upload_inventory_in_bucket()
    upload_payment_in_bucket()
    upload_restaurant_location_in_bucket()
    upload_shift_detail_in_bucket()
    upload_staff_in_bucket()
    upload_technical_metadata_in_bucket()
    upload_transaction_item_in_bucket()
    upload_transaction_in_bucket()
