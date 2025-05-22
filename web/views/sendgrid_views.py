# email_app/views.py
import os
import json
import requests
from django.utils.crypto import get_random_string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from web.models import OTP
from django.contrib.auth import get_user_model
from web.utils.email_verification import get_model_instance_by_email

User = get_user_model()

class SendEmailVerificationView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        user_id = self.request.user.pk

        if not email or not user_id:
            return Response({'error': 'email and user_id are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)

        otp_code = get_random_string(6, '0123456789')
        otp = OTP.objects.create(user=user, email=email, otp_code=otp_code)

        # Make sure to encode email if needed
        email_encoded = requests.utils.quote(email)

        # Construct the activation link
        domain = "beta.xblock.ai"
        activation_url = f"/api/verify-email/?otp={otp_code}&email={email_encoded}"

        # Email template
        email_template = """
        Hi {username},

        Thank you for registering at xBlock. Please click the link below to activate your account:

        http://{domain}{activation_url}

        If you did not make this request, you can ignore this email.

        Thanks,
        xBlock Team
        """

        email_body = email_template.format(
            username=user.username,
            domain=domain,
            activation_url=activation_url
        )

        message = {
            "personalizations": [
                {
                    "to": [
                        {"email": email}
                    ],
                    "subject": "Activate Your xBlock Account"
                }
            ],
            "from": {"email": "devops@xblock.ai"},
            "content": [
                {
                    "type": "text/plain",
                    "value": email_body
                }
            ],
            "tracking_settings": {
                "click_tracking": {"enable": False},
                "open_tracking": {"enable": False}
            }
        }

        try:
            sg_api_key = os.getenv('SENDGRID_API_KEY')
            response = requests.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={
                    "Authorization": f"Bearer {sg_api_key}",
                    "Content-Type": "application/json"
                },
                data=json.dumps(message)
            )
            if response.status_code == 202:
                return Response({'status': 'verification email sent'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': response.text}, status=response.status_code)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyEmailView(APIView):
    def get(self, request, *args, **kwargs):
        otp_code = request.query_params.get('otp')
        email = request.query_params.get('email')

        if not otp_code or not email:
            return Response('Invalid verification link', status=400)

        try:
            otp = OTP.objects.get(email=email, otp_code=otp_code)
            if otp.is_valid():
                instance = get_model_instance_by_email(email)
                if instance:
                    if isinstance(instance, User):
                        if instance.email == email:
                            instance.is_email_verified = True
                        elif instance.secondary_email == email:
                            instance.is_secondary_email_verified = True
                    else:
                        instance.is_email_verified = True
                    instance.save()
                    return Response('Email verified successfully', status=200)
                else:
                    return Response('No instance found for the given email', status=400)
            else:
                return Response('OTP is invalid or expired', status=400)
        except OTP.DoesNotExist:
            return Response('Invalid verification link', status=400)