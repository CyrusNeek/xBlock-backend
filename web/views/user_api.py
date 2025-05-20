# accounts/views.py
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from web.serializers import UserSerializer, UserRegistrationSerializer, UserUpdateSerializer, UserWizardSerializer
from web.models import User, QueueEmail, Unit, BrandOwner
from django.core.exceptions import ObjectDoesNotExist
import random
from vtk.services import get_presigned_post_url, upload_file_to_gcs
from rest_framework.permissions import IsAuthenticated
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import sendgrid
from sendgrid.helpers.mail import Mail
from xblock import settings as xblock_settings


@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        serializer = UserRegistrationSerializer(data=request.data)
        
        try:
            if serializer.is_valid():
                user = serializer.save()
                # send_register_verification_email(user)
                sent_email = send_otp_email_directly(user.email, user.otp_secret, "d-1d8ced4f741c460d8f4b5db2a7de5bc4", "Verify")
                if not sent_email["status"] == 202:
                    return Response({'error': sent_email["message"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


                return Response({'message': 'Please check your email for verification'}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except IntegrityError as e:
            if 'unique constraint' in str(e):
                return Response({'error': 'Username or email already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({'error': 'An integrity error occurred: ' + str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['PATCH'])
@permission_classes([IsAuthenticated]) 
def update_user(request):
    if request.method == 'PATCH':
        user = request.user

        serializer = UserUpdateSerializer(instance=user, data=request.data, partial=True)

        uploaded_file = request.FILES.get("file")
        if uploaded_file:
            filename = f"public/{user.first_name}_{user.id}.jpg".replace(" ", "_")
            presigned_url, data = get_presigned_post_url(filename)
            
            uploaded = upload_file_to_gcs(presigned_url, data, uploaded_file)
            if not uploaded:
                return Response({"error": "File upload failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            user.profile_image_url = filename

        if serializer.is_valid():
            serializer.save()  
            return Response(
                {"message": "User updated successfully", "user": serializer.data},
                status=status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"error": "Invalid request method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
                

@api_view(['POST'])
def resend_otp(request):
    """
    Resend OTP to the user's email if the user exists.
    """
    if request.method == 'POST':
        email = request.data.get('email')  # Get the email from the request

        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=email)
            user.otp_secret = generate_otp_secret()
            user.save()
            sent_email = send_otp_email_directly(email, user.otp_secret, "d-87c580ad6eb94097a9f54dc41b256acc", "Verify")
            if not sent_email["status"] == 202:
                return Response({'error': sent_email["message"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({'message': 'OTP has been resent to your email.'}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': f'Something went wrong: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_wizard_status(request):
    """
    Update user wizard status each time the user advances in their steps.
    """
    if request.method == 'PATCH':
        wizard_status = request.data.get('wizard_status')

        if not wizard_status:
            return Response({'error': 'Wizard status is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            serializer = UserWizardSerializer(instance=request.user, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "message": "Wizard status updated successfully.",
                        "user": serializer.data
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {'error': f'An unexpected error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

def send_verification_email(user):
    QueueEmail.objects.create(
                    email=user.email,
                    subject="Verify",
                    message="",
                    status=1,  # Pending
                    type="template", # === template
                    template_id= "d-87c580ad6eb94097a9f54dc41b256acc", # from sendgrid
                    entry_data={
                        "code" : user.otp_secret
                    },
                    sender_email="xBlock <otp-noreply@xblock.ai>"
                )

def send_register_verification_email(user):
    QueueEmail.objects.create(
                    email=user.email,
                    subject="Verify",
                    message="",
                    status=1,  # Pending
                    type="template", # === template
                    template_id= "d-1d8ced4f741c460d8f4b5db2a7de5bc4", # from sendgrid
                    entry_data={
                        "code" : user.otp_secret
                    },
                    sender_email="xBlock <otp-noreply@xblock.ai>"
                )
    
def generate_otp_secret(length=6):
    """Generate a random OTP secret of the specified length (default is 6 digits)."""
    otp_secret = ''.join(random.choices('0123456789', k=length))
    return otp_secret




@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def send_welcome_email(request):
    if request.method == 'POST':
        try:
            template_id = "d-009e4ff3f5ed48499bd3e0c3062a4b74" # for business
            user = request.user
            if user.account_type == 1 :
                template_id = "d-d7f5141b23884e258b8e62e500e15765" # for personal
            QueueEmail.objects.create(
                email=user.email,
                subject="Welcome to xBlock",
                message="",
                status=1,  # Pending
                type="template", # === template
                template_id= template_id, # from sendgrid
                entry_data={
                    "user": user.name
                },
            )
            return Response(
                        {
                            "message": "Email sent successfully"
                        },
                        status=status.HTTP_200_OK
                    )
        except Exception as e:
            return Response(
                {'error': f'Failed to send welcome email: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    return Response({"error": "Invalid request method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

def send_otp_email_directly(email, otp_code, template_id="d-87c580ad6eb94097a9f54dc41b256acc", subject="Verify"):
    """
    Send OTP email directly using SendGrid without using queue
    
    Args:
        email (str): Recipient email address
        otp_code (str): The OTP code to send
        template_id (str): SendGrid template ID (default is verification template)
        subject (str): Email subject (default is "Verify")
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    message = Mail(
        from_email="xBlock <otp-noreply@xblock.ai>",
        to_emails=email,
        subject=subject,
        plain_text_content=None
    )
    
    # Set template ID and dynamic data
    message.template_id = template_id
    message.dynamic_template_data = {
        "code": otp_code
    }
    
    try:
        sg = sendgrid.SendGridAPIClient(xblock_settings.SENDGRID_API_KEY)
        response = sg.send(message)
        if response.status_code == 202:

            return {
                "message": "OTP email sent successfully",
                "status": response.status_code
            }
        return {
            "message": "Failed to send OTP email",
            "status": response.status_code
        }
    except Exception as e:
        return {
            "message": f"Failed to send OTP email: {str(e)}",
            "status": 500
        }