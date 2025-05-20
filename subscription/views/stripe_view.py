from decimal import Decimal
import stripe
import logging
import json
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from web.models.user import User
from subscription.models import Invoice, SubscriptionPlan
from datetime import datetime

from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from subscription.services.user_subscription_service import UserSubscriptionService

stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)
User = get_user_model()

class WebhookReceivedView(APIView):

    def get_stripe_invoice_plan_data(self, invoice_id):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            invoice = stripe.Invoice.retrieve(invoice_id)
            return invoice
        except stripe.error.StripeError as e:
            logger.error(f"Stripe API Error: {e}")
            return None

    def post(self, request, *args, **kwargs):
        logger.info(f"Received headers: {request.headers}")
        logger.info(f"Received payload: {request.body.decode('utf-8')}")

        endpoint_secret = settings.WEBHOOK_API_KEY
        payload = request.body.decode("utf-8")
        signature = request.headers.get("stripe-signature")

        if not signature:
            logger.error("Stripe signature is missing")
            return Response({"error": "Missing Stripe Signature"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            event = stripe.Webhook.construct_event(payload, signature, endpoint_secret)
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid Stripe signature")
            return Response({"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            return Response({"error": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        event_type = event.get("type")
        event_data = event.get("data", {}).get("object", {})
        client_reference_id = event_data.get("client_reference_id")

        if not client_reference_id:
            logger.error(f"Missing client_reference_id in event: {json.dumps(event, indent=2)}")
            return Response({"error": "client_reference_id is missing"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            client = User.objects.get(pk=int(client_reference_id))
        except User.DoesNotExist:
            logger.error(f"User with id {client_reference_id} not found")
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        invoice_data = None
        if event_type == "checkout.session.completed":
            invoice_id = event_data.get("invoice")
            if not invoice_id:
                logger.error("Invoice ID is missing from the event data")
                return Response({"error": "Invoice ID is missing"}, status=status.HTTP_400_BAD_REQUEST)

            invoice_data = self.get_stripe_invoice_plan_data(invoice_id)
            if invoice_data is None:
                return Response({"error": "Failed to retrieve invoice data"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        event_str = json.dumps(event, indent=2)  # Define the missing variable

        obj_invoice = Invoice()
        obj_invoice.service = Invoice.ServiceChoices.STRIPE
        obj_invoice.payload = event_str
        obj_invoice.client = client
        obj_invoice.payment_status = event_type

        if invoice_data:
            obj_invoice.customer = invoice_data.get("customer", "")
            obj_invoice.customer_email = invoice_data.get("customer_email", "")
            obj_invoice.invoice_pdf = invoice_data.get("invoice_pdf", "")
            obj_invoice.number = invoice_data.get("number", "")
            obj_invoice.period_start = datetime.fromtimestamp(invoice_data.get("period_start", 0))
            obj_invoice.period_end = datetime.fromtimestamp(invoice_data.get("period_end", 0))
            obj_invoice.tax = Decimal(invoice_data.get("tax") or 0)  # Avoid Decimal(None) issue
            obj_invoice.total = Decimal(invoice_data.get("total") or 0)  # Avoid Decimal(None) issue

        obj_invoice.save()

        subscription_id = event_data.get("subscription")
        subscription_data = stripe.Subscription.retrieve(subscription_id)
        product_id = subscription_data["items"]["data"][0]["plan"]["product"]

        plan = SubscriptionPlan.objects.filter(stripe_id=product_id).first()
        if plan:
            user_subscription = UserSubscriptionService(client, client.affiliation)
            user_subscription.create_user_subscription_from_plan(plan)

        return Response({"status": "success"}, status=status.HTTP_200_OK)

   
    

class CreateCustomerPortalSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            customer_id = user.stripe_customer_id

            if not customer_id:
                customer_id = self.get_or_create_stripe_customer(user)

            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url="https://app.xblock.ai/setting/plans-payment",
            )

            return Response({"url": session.url}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
        
    def get_or_create_stripe_customer(self, user):
        if not user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=user.email,
                name=f"{user.first_name} {user.last_name}",
                metadata={"user_id": user.id}  
            )
            user.stripe_customer_id = customer.id
            user.save()
        return user.stripe_customer_id


