import stripe 
from web.models import User 
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

class Stripe_Service:
    
    @staticmethod
    def get_or_create_stripe_customer(user: User ):
            if not user.stripe_customer_id:
                customer = stripe.Customer.create(
                    email=user.email,
                    name=f"{user.first_name} {user.last_name}",
                    metadata={"user_id": user.id}  
                )
                
            return customer.id
    
    @staticmethod
    def create_subscription(plan, user : User):
        price = stripe.Price.create(
            unit_amount=int(plan.subscription_price * 100),  
            currency="usd",
            recurring={"interval": "month"},  
            product=plan.stripe_id,
        )


        stripe_subscription = stripe.Subscription.create(
            customer=user.stripe_customer_id,
            items=[{"price": price.id}],  
            trial_period_days=14,
            expand=["latest_invoice.payment_intent"],
        )
        return stripe_subscription