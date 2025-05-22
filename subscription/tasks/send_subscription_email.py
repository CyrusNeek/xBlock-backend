from celery import shared_task
from subscription.models import UserSubscription, SubscriptionPlan, SubscriptionEmail
from django.utils import timezone
from web.models import User, QueueEmail
import json
from django.contrib.auth import get_user_model

import logging

logger = logging.getLogger(__name__)


# @shared_task
# def send_subscription_email():
#     now = timezone.now()
#     users = User.objects.filter(is_super_user=True, is_active=True).all()
#     emails = SubscriptionEmail.objects.all()
#     user_subscriptions = UserSubscription.objects.filter( user__in=users).all()
#     now_clock = now.time()  

#     for user_subscription in user_subscriptions:

#         for email in emails:
#             if email.send_time == "BEFORE":
#                 days_difference = (user_subscription.end_date - now).days  
#                 if days_difference == email.days:
#                     if now_clock >= email.send_clock:
#                         if user_subscription.email_ids:
#                             try:
#                                 sent_emails = json.loads(user_subscription.email_ids)
#                                 found_match = None
#                                 for sent_email in sent_emails:
#                                     if sent_email["email_id"] == email.id:
#                                         found_match = True
#                                         break
#                                 if found_match:
#                                     break
#                             except json.JSONDecodeError:
#                                 sent_emails = []
#                         else:
#                             sent_emails = []
#                         email_date = {}
#                         email_date["email_id"] = email.id 
#                         email_date["sending date"] = f"{now} + {now_clock}" 
#                         sent_emails.append(email_date)
#                         user_subscription.email_ids = json.dumps(sent_emails)
#                         user_subscription.save()
#                         print(days_difference)
#                         print("matched") 
#                     else:
#                         print("now clock is less than")
#                 else:
#                     print(days_difference)


def get_current_time():
    now = timezone.now()
    return now, now.time()

def get_active_superusers():
    return User.objects.filter(is_super_user=True, is_active=True).all()

def get_all_emails():
    return SubscriptionEmail.objects.all()

def get_user_subscriptions(users):
    return UserSubscription.objects.filter(user__in=users,status="active").all()

def has_email_been_sent(user_subscription, email):
    if user_subscription.email_ids:
        try:
            sent_emails = json.loads(user_subscription.email_ids)
            for sent_email in sent_emails:
                if sent_email.get("email_id") == email.id:
                    return True
        except json.JSONDecodeError:
            return False
    return False

def record_email_sent(user_subscription, email, now, now_clock):
    email_record = {
        "email_id": email.id,
        "email_title": email.title,
        "sending_date": f"{now} + {now_clock}"
    }
    if user_subscription.email_ids:
        try:
            sent_emails = json.loads(user_subscription.email_ids)
        except json.JSONDecodeError:
            sent_emails = []
    else:
        sent_emails = []
    sent_emails.append(email_record)
    user_subscription.email_ids = json.dumps(sent_emails)
    user_subscription.save()

def process_email_for_subscription(user_subscription, email, now, now_clock):

    if email.send_time == "BEFORE":
        days_difference = (user_subscription.end_date - now).days
        if days_difference != email.days:
            return
    if email.send_time == "AFTER":
        days_difference = (now - user_subscription.end_date).days
        print(days_difference)
        if days_difference != email.days:
            return
    if email.send_time == "SAME":
        days_difference = (user_subscription.end_date - now ).days
        print(days_difference)
        if days_difference != 0 :
            return
    
    if now_clock < email.send_clock:
        print("now clock is less than email.send_clock")
        return
    
    if has_email_been_sent(user_subscription, email):
        return

    record_email_sent(user_subscription, email, now, now_clock)

    if user_subscription.user.account_type == 2 :
        template_id = email.personal_email_template_id
    else:
        template_id = email.business_email_template_id
        
    add_subscription_email_to_queue(user_subscription.user, template_id, email.days, user_subscription.sender_email)
    print(days_difference)
    print("matched")


@shared_task
def send_subscription_email():
    now, now_clock = get_current_time()
    users = get_active_superusers()
    emails = get_all_emails()
    user_subscriptions = get_user_subscriptions(users)

    for user_subscription in user_subscriptions:
        for email in emails:
            process_email_for_subscription(user_subscription, email, now, now_clock)
            




def add_subscription_email_to_queue(user, template_id, days, sender):
    QueueEmail.objects.create(
                    email=user.email,
                    subject="Subscription",
                    message="",
                    status=1,  # Pending
                    type="template", # === template
                    template_id= template_id, # from sendgrid
                    entry_data={
                        "days" : days
                    },
                    sender_email=sender
                )

                

