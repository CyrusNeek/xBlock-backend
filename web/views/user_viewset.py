import json
import pandas as pd
import string
import secrets
from django.db.models import Prefetch
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from roles.serilalizers import SimpleUserRoleSerializer
from web.models import User, QueueEmail, Unit, BrandOwner
from web.serializers import UserSerializer
from roles.models import Role
from roles.constants import SET_ROLE_USER_ACCESS, UNLIMITED_CRUD_TEAM_ACCESS
from roles.permissions import UserPermission
from roles.assigne_role_permission import assigne_role_permission
import logging

from subscription.models import UserSubscription, SubscriptionPlan, MembershipBonus

from roles.constants import (
    LIMITED_ANSWER_ACCESS,
    UNLIMITED_ANSWER_ACCESS,
    ACTIVE_MEETING_ACCESS,
    XCLASSMATE_ACCESS,
    UNLIMITED_CRUD_BLOCK_ACCESS,
)
# from web.views.auth import User

logger = logging.getLogger(__name__)

def generate_random_password(length=12):
    """
    Generates a random password with a mix of uppercase, lowercase, digits, and punctuation.
    :param length: Length of the password (default is 12)
    :return: Randomly generated password string
    """

    # Define the character sets
    alphabet = string.ascii_letters  # Uppercase + lowercase
    digits = string.digits  # Digits (0-9)
    # Special characters (e.g., @, #, $, etc.)
    punctuation = string.punctuation

    # Ensure the password contains at least one of each category (uppercase, lowercase, digit, special character)
    password = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(digits),
        secrets.choice(punctuation),
    ]

    # Fill the remaining characters randomly from the combined set of all characters
    password += [
        secrets.choice(alphabet + digits + punctuation) for _ in range(length - 4)
    ]

    # Shuffle the result to ensure randomness in placement of different characters
    secrets.SystemRandom().shuffle(password)

    # Join the list to make a string
    return "".join(password)


class UserViewSet(viewsets.ModelViewSet):
    """
    List: list users within request.user's brands
    Create: Create a new user if the requester has the necessary permissions.
    Delete: Delete a user if the requester has the necessary permissions.
    """

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = (
        User.objects.select_related("unit", "role")
        .prefetch_related(
            "units",
            Prefetch(
                "role",
                queryset=Role.objects.prefetch_related("permissions", "block_category"),
            ),
        )
        .all()
    )

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            return self.queryset.none()

        elif user.role.is_superuser:
            return self.queryset.filter(affiliation=user.affiliation).distinct()

        elif UserPermission.check_user_permission(
            self.request.user, UNLIMITED_CRUD_TEAM_ACCESS
        ):
            return self.queryset.filter(units__in=user.all_units).distinct('id')

        return self.queryset.filter(pk=user.pk)

    def check_permission(self, request):
        return UserPermission.check_user_permission(
            request.user, UNLIMITED_CRUD_TEAM_ACCESS
        )

    def has_role_assignment_permission(self, user):
        return UserPermission.check_user_permission(user, SET_ROLE_USER_ACCESS)

    def perform_permissions_check(self, request):
        if not self.check_permission(request):
            raise PermissionDenied("You don't have permission to perform this action.")

    def create(self, request, *args, **kwargs):
        self.perform_permissions_check(request)
        user = request.user
        data = request.data.copy()

        # create user brand instance using affiliation field
        # UserBrand.objects.create(user=user, brand=)

        if not self.has_role_assignment_permission(user):
            data.pop(
                "role", None
            )  # Set role to None if the user doesn't have the permission to assign roles
            
        assigned_role = assigne_role_permission(user.id, data.get("role")) or None

        if assigned_role:
            try:
                plan = UserSubscription.objects.get(
                    brand_owner=user.affiliation, status=UserSubscription.ACTIVE
                )
            except UserSubscription.DoesNotExist:
                raise ValidationError("No active subscription found for this user.")

            if "token" in assigned_role:
                if plan.token_user_limit > 0:
                    plan.token_user_limit -= 1
                else:
                    raise ValidationError("Token limit exceeded.")

            if "meeting" in assigned_role:
                if plan.meeting_user_limit > 0:
                    plan.meeting_user_limit -= 1
                else:
                    raise ValidationError("Meeting limit exceeded.")

            if "classmate" in assigned_role:
                if plan.classmate_user_limit > 0:
                    plan.classmate_user_limit -= 1
                else:
                    raise ValidationError("Classmate limit exceeded.")

            if "upload" in assigned_role:
                if plan.upload_user_limit > 0:
                    plan.upload_user_limit -= 1
                else:
                    raise ValidationError("Upload limit exceeded.")

            # Save the updated limits
            plan.save()
        else:
            raise ValidationError(
                "You cannot set this role to this user. Please check your notifications on the website."
            )

        if user.role.is_superuser:
            # Check if the user is trying to add a member to their own affiliation
            if (
                "affiliation" in data
                and int(data["affiliation"]) != user.affiliation.id
            ):
                raise ValidationError(
                    "You can only add members to your own affiliation."
                )
        # Check if the user is trying to add a member to their own units
        if "units" in data:
            unit_ids = data["units"]
            if not user.units.filter(id__in=unit_ids).count() == len(unit_ids):
                raise ValidationError("You can only add members to your own units.")

        membership_bonus = MembershipBonus.objects.first()
        if membership_bonus:
            data["tokens"] = membership_bonus.tokens
            data["minutes"] = membership_bonus.minutes
        else:
            data["tokens"] = 0
            data["minutes"] = 0
        password = generate_random_password()
        data["password"] = password
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        html_content = render_to_string(
            "emails/welcome_email.html", {"user": serializer.data, "password": password}
        )
        # Fallback to plain text content
        plain_text_content = strip_tags(html_content)
        print(data)
        QueueEmail.objects.create(
            email=data["email"],
            subject="Welcome to xBlock",
            message=plain_text_content,
            status=1,  # Pending
            type="template", # === template
            template_id= "d-b7fa12f53aac4249a67a497e7b74220f", # from sendgrid
            entry_data={
                "username": str(data["username"]),
                "password": str(password),
                "user": str(data["first_name"])
            },
        )
        allocate_brand_user_usages(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        self.perform_permissions_check(request)
        user = request.user
        data = request.data.copy()  # Create a mutable copy of the data

        if not self.has_role_assignment_permission(user):
            data.pop(
                "role", None
            )  # Set role to None if the user doesn't have the permission to assign roles

        assigned_role = assigne_role_permission(user.id, data.get("role")) or None

        if assigned_role:
            try:
                plan = UserSubscription.objects.get(
                    brand_owner=user.affiliation, status=UserSubscription.ACTIVE
                )
            except UserSubscription.DoesNotExist:
                raise ValidationError("No active subscription found for this user.")

            if "token" in assigned_role:
                if plan.token_user_limit > 0:
                    plan.token_user_limit -= 1
                else:
                    raise ValidationError("Token limit exceeded.")

            if "meeting" in assigned_role:
                if plan.meeting_user_limit > 0:
                    plan.meeting_user_limit -= 1
                else:
                    raise ValidationError("Meeting limit exceeded.")

            if "classmate" in assigned_role:
                if plan.classmate_user_limit > 0:
                    plan.classmate_user_limit -= 1
                else:
                    raise ValidationError("Classmate limit exceeded.")

            if "upload" in assigned_role:
                if plan.upload_user_limit > 0:
                    plan.upload_user_limit -= 1
                else:
                    raise ValidationError("Upload limit exceeded.")

            # Save the updated limits
            plan.save()
        else:
            raise ValidationError(
                "You cannot set this role to this user. Please check your notifications on the website."
            )

        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        self.perform_permissions_check(request)
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=["get"])
    def get_users_manager(self, request):
        data = self.get_queryset().values("id", "username")
        return JsonResponse(list(data), safe=False)

    # get Excel file from file (from front) and return the data inside excel file

    @action(detail=False, methods=["post"])
    def upload_excel(self, request):
        excel_file = request.FILES["file"]
        self.perform_permissions_check(request)
        user = request.user
        data = request.data.copy()

        # create user brand instance using affiliation field
        # UserBrand.objects.create(user=user, brand=)
        if isinstance(data["units"], str):
            data["units"] = json.loads(data["units"])

        if not self.has_role_assignment_permission(user):
            data.pop(
                "role", None
            )  # Set role to None if the user doesn't have the permission to assign roles

        assigned_role = assigne_role_permission(user.id, data.get("role")) or None

        if assigned_role:
            try:
                plan = UserSubscription.objects.get(
                    brand_owner=user.affiliation, status=UserSubscription.ACTIVE
                )
            except UserSubscription.DoesNotExist:
                raise ValidationError("No active subscription found for this user.")

            if "token" in assigned_role:
                if plan.token_user_limit > 0:
                    plan.token_user_limit -= 1
                else:
                    raise ValidationError("Token limit exceeded.")

            if "meeting" in assigned_role:
                if plan.meeting_user_limit > 0:
                    plan.meeting_user_limit -= 1
                else:
                    raise ValidationError("Meeting limit exceeded.")

            if "classmate" in assigned_role:
                if plan.classmate_user_limit > 0:
                    plan.classmate_user_limit -= 1
                else:
                    raise ValidationError("Classmate limit exceeded.")

            if "upload" in assigned_role:
                if plan.upload_user_limit > 0:
                    plan.upload_user_limit -= 1
                else:
                    raise ValidationError("Upload limit exceeded.")

            # Save the updated limits
            plan.save()
        else:
            raise ValidationError(
                "You cannot set this role to this user. Please check your notifications on the website."
            )
    
        if user.role.is_superuser:
            # Check if the user is trying to add a member to their own affiliation
            if (
                "affiliation" in data
                and int(data["affiliation"]) != user.affiliation.id
            ):
                raise ValidationError(
                    "You can only add members to your own affiliation."
                )
        # Check if the user is trying to add a member to their own units
        if "units" in data:
            unit_ids = data["units"]
            if not user.units.filter(id__in=unit_ids).count() == len(unit_ids):
                raise ValidationError("You can only add members to your own units.")

        membership_bonus = MembershipBonus.objects.first()
        if membership_bonus:
            data["tokens"] = membership_bonus.tokens
            data["minutes"] = membership_bonus.minutes
        else:
            data["tokens"] = 0
            data["minutes"] = 0

        # read the excel file and return the data with pandas
        data_excel = pd.read_excel(excel_file)

        # get all rows without header
        rows = data_excel.values
        users_exist = []
        user_created = []
        user_created_email = []
        for row in rows:
            if User.objects.filter(email=row[2]).exists():
                print(f"User with email {row[2]} already exists")
                users_exist.append(row[2])
                continue
            # create new User instance
            # generate random password for user
            password = generate_random_password()
            user = User()
            user.first_name = row[0]
            user.last_name = row[1]
            user.email = row[2]
            user.username = row[2]
            user.phone_number = row[3]
            user.password = password
            print("data:", data)
            if "role" in data:
                user.role = Role.objects.get(pk=data["role"])
            if "affiliation" in data:
                user.affiliation = data["affiliation"]
            user.save()
            print("user id:", user.pk)
            # units is many to many field assigne units in user
            if "units" in data:
                user.units.set(data["units"])

            user_created_email.append(row[2])
            user_created.append(user.email)
            # Create an email queue entry for this new user
            # Render the HTML template
            html_content = render_to_string(
                "emails/welcome_email.html", {"user": user, "password": password}
            )
            # Fallback to plain text content
            plain_text_content = strip_tags(html_content)

            QueueEmail.objects.create(
                email=user.email,
                subject="Welcome to xBlock",
                message=plain_text_content,
                status=1,  # Pending
            )
            print(f"User with email {row[2]} created successfully")

        # return the data
        return Response(data={"users_exist": users_exist, "user_created": user_created})

    # an custom endpoint get list users just fields firstname lastname role name and status
    @action(detail=False, methods=["get"])
    def get_list_users(self, request):
        data = self.get_queryset().values(
            "id", "first_name", "last_name", "role", "is_active", "email","units", "phone_number","manager_id", "team"
        )
        return JsonResponse(list(data), safe=False)

    # an custom endpoint get role of user
    @action(detail=False, methods=["get"])
    def get_role(self, request, pk=None):
        user = request.user
        role_data = SimpleUserRoleSerializer(user.role).data
        return JsonResponse({"role": role_data}, safe=False)
    



def allocate_brand_user_usages(data ):
    user = User.objects.get(pk=data["id"])
    brand_owner = BrandOwner.objects.get(pk=data["affiliation"])
    user_subscription = UserSubscription.objects.get(brand_owner=brand_owner.pk)
    plan = SubscriptionPlan.objects.get(pk=user_subscription.plan.pk)


    xbrain_permissions = [
        LIMITED_ANSWER_ACCESS,
        UNLIMITED_ANSWER_ACCESS,
    ]
    
    upload_permissions = [UNLIMITED_CRUD_BLOCK_ACCESS]

    classmate_permissions = [XCLASSMATE_ACCESS]

    meeting_permissions = [ACTIVE_MEETING_ACCESS]

    meeting_limits = 0
    classmate_limits = 0
    token_limits = 0
    upload_limits = 0

    
    user_permissions = list(
        user.role.permissions.values_list("component_key", flat=True)
    )

    if any(permission in user_permissions for permission in xbrain_permissions):
        if plan.token_user_limit >= token_limits:
            user.tokens = plan.total_token_allocation
            token_limits += 1

    if any(permission in user_permissions for permission in meeting_permissions):
        if plan.meeting_user_limit >= meeting_limits:
            user.xmeeting_minutes = plan.total_meeting_duration
            meeting_limits += 1

    if any(permission in user_permissions for permission in classmate_permissions):
        if plan.classmate_user_limit >= classmate_limits:
            user.stk_minutes = plan.total_classmate_session_duration
            classmate_limits += 1
            
    if any(permission in user_permissions for permission in upload_permissions):
        if plan.upload_user_limit >= upload_limits:
            user.upload_size = plan.total_upload_allocation
            upload_limits += 1
            
    user.save(update_fields=["tokens", "xmeeting_minutes", "stk_minutes", "upload_size"])

    logger.info("user allocations updated successfully")