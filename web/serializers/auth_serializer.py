from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from datetime import timedelta
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from roles.serilalizers import RoleSerializer
from web.models import BrandOwner, Brand, UserBrand
from roles.models import Role, Permission
from subscription.models.user_subscription import UserSubscription, SubscriptionPlan



from web.services import initialize_user_account, provide_access_token, validate_account_is_not_susspended

User = get_user_model()


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        token["email"] = user.email
                # add role and user id
        token["full_name"] = user.full_name
        token["display_name"] = user.display_name
        role_serializer = RoleSerializer(user.role)
        # token["role"] = role_serializer.data

        return token

    def validate(self, attrs):
        # The default result (access and refresh tokens)
        data = super().validate(attrs)

        # Add additional user information to the response
        data["first_name"] = self.user.first_name
        data["last_name"] = self.user.last_name
        data["user_id"] = self.user.pk
        return data
    
class OtpTokenObtainPairSerializer(TokenObtainPairSerializer):
    password = serializers.CharField(required=True)
    username = serializers.CharField(required=True)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        token["email"] = user.email
        token["full_name"] = user.full_name
        token["display_name"] = user.display_name


        return token
    
    def provide_demo_account(self, username, otp_secret):
        if username == 'demo@xblock.ai' and otp_secret == "224466":
            user = get_user_model().objects.filter(username=username).first()
            initialize_user_account(user)

            data = provide_access_token(user)
            return data
        else:
            raise AuthenticationFailed("Invalid OTP secret or OTP has expired.")

    def validate(self, attrs):
        otp_secret = attrs.get("password") # didnt change password to prevent front update
        username = attrs.get("username")

        if username == 'demo@xblock.ai':
            return self.provide_demo_account(username, otp_secret)

        if not otp_secret or not username:
            raise AuthenticationFailed("OTP secret and username are required.")

        user = get_user_model().objects.filter(username=username).first()

        self.validate_user_exist(user)
        
        if not self.is_valid_otp(user, otp_secret):
            self.increase_attempt(user)
            raise AuthenticationFailed("Invalid OTP secret or OTP has expired.")

       
        validate_account_is_not_susspended(user)
        
        initialize_user_account(user)

        self.reset_otp(user)

        data = provide_access_token(user)
        return data

    def is_valid_otp(self, user, otp_secret):
        if user.otp_secret != otp_secret:
            return False
        
        if not user.otp_expire or timezone.now() > user.otp_expire:
            return False
        
        if user.otp_attempts >= 3:
            raise AuthenticationFailed("Too many failed OTP attempts. Please try again later.")
        
        return True

    def increase_attempt(self, user):
        user.otp_attempts += 1
        user.save()

    def reset_otp(self, user):
        user.otp_attempts = 0
        user.save()

    def validate_user_exist(self, user):
        if not user:
            raise AuthenticationFailed("User not found.")

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    phone_number = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = (
            "password",
            "password2",
            "email",
            "first_name",
            "last_name",
            "phone_number",
        )

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        return attrs

    def validate_email(self, value):
        # Check if the email already exists
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        user = User.objects.create(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            username=validated_data["email"],
            phone_number=validated_data["phone_number"],
        )
        user.set_password(validated_data["password"])

        user.save()

        return user

