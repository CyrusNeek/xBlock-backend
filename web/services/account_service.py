from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from subscription.services.stripe_service import Stripe_Service

def initialize_user_account(user):
    if user.is_email_verified is True:
        return
    activate_user(user)
    brandOwner = create_brand_owner(user)
    create_stripe_customer(user)
    set_user_brand_owner(user,brandOwner)
    plan = get_trial_plan(user)
    create_user_subscription(user, brandOwner, plan)
    activate_free_trial(user)
    role = create_administrator_role(user, brandOwner)
    set_role_permissions(role)
    set_user_role(user, role)
    allocate_brand_user_usages(user, plan)
    brand , sub_brand = create_brand(user, brandOwner)
    create_user_brand(user, brand)
    create_user_brand(user, sub_brand)
    set_role_name(role, brand)
    unit = create_unit(brand)
    set_user_unit(user,unit)
    sub_unit = create_unit(sub_brand)
    set_user_unit(user,sub_unit)


def allocate_brand_user_usages(user, plan):
    from roles.constants import (
        LIMITED_ANSWER_ACCESS,
        UNLIMITED_ANSWER_ACCESS,
        ACTIVE_MEETING_ACCESS,
        XCLASSMATE_ACCESS,
        UNLIMITED_CRUD_BLOCK_ACCESS,
    )

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


def create_brand_owner(user):
    from web.models import BrandOwner

    brandOwner = BrandOwner()
    brandOwner.name = user.name
    brandOwner.email = user.email
    brandOwner.is_email_verified = True
    brandOwner.save()
    return brandOwner

def set_user_brand_owner(user, brand_owner):
    user.affiliation = brand_owner
    user.save()


def get_trial_plan(user):
    from subscription.models.user_subscription import SubscriptionPlan

    if user.account_type == 2 :
        plan = SubscriptionPlan.objects.filter(pk=6).first()
    else:
        plan = SubscriptionPlan.objects.filter(pk=12).first()

    return plan


def create_user_subscription(user, brandOwner, plan):
    from subscription.models.user_subscription import UserSubscription
    from subscription.services.user_subscription_service import UserSubscriptionService

    subscription_service = UserSubscriptionService(user, brandOwner)
    user_subscription = subscription_service.create_user_subscription_from_plan(plan)

    # stripe_subscription = Stripe_Service.create_subscription(plan, user)
    # user_subscription.stripe_id = stripe_subscription.id 
    user_subscription.save()
    return user_subscription

def create_stripe_customer(user):
    customer_id = Stripe_Service.get_or_create_stripe_customer(user)
    user.stripe_customer_id = customer_id
    user.save()


def create_administrator_role(user, brandOwner):
    from roles.models import Role
    role = Role()
    role.brand_owner = brandOwner
    role.creator = user
    role.is_active = True
    role.is_immuteable=True
    role.save()
    return role

def set_role_name(role, brand):
    role.label = "Super Admin "
    role.save()


def set_role_permissions(role):
    from roles.models import Permission

    permission_keys = [
        "ua_block",
        "ua_crud_brand",
        "ua_crud_block",
        "ua_task_analytics",
        "set_role_user",
        "ua_VTK_analytics",
        "pa_meeting_analytics",
        "pa_VTK_analytics",
        "ua_meeting_analytics",
        "a_VTK",
        "a_meeting",
        "ua_crud_role",
        "ua_conversation_analytics",
        "pa_meeting_crud_task",
        "ua_answer",
        "pa_conversation",
        "ua_order_info",
        "ua_crud_team",
        "ua_guest_profile",
    ]

    existing_permissions = Permission.objects.filter(component_key__in=permission_keys)
    role.permissions.set(existing_permissions)
    role.save()


def set_user_role(user, role):
    user.role = role
    user.save()

def set_user_unit(user, unit):
    from web.models import User
    user.unit = unit
    user.units.add(unit)
    user.save()


def create_unit(brand):
    from web.models import Unit
    unit = Unit()
    unit.brand = brand
    unit.save()
    return unit


def create_brand(user, brandOwner):
    from web.models import Brand

    brand = Brand()
    brand.owner = brandOwner
    brand.admin_name = user.first_name 
    brand.save()

    sub_brand = Brand()
    sub_brand.owner = brandOwner
    sub_brand.affiliation = brand
    sub_brand.admin_name = user.first_name 

    sub_brand.save()
    return brand , sub_brand
    


def create_user_brand(user, brand):
    from web.models import UserBrand

    user_brand = UserBrand()
    user_brand.user = user
    user_brand.brand = brand
    user_brand.save()
    return user_brand


def validate_account_is_not_susspended(user):
    from rest_framework.exceptions import AuthenticationFailed

    if not user.is_active and user.is_email_verified:
        raise AuthenticationFailed(
            "Your account is suspended, please contact your administrator"
        )


def provide_access_token(user):
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(user)
    data = {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }
    return data


def activate_user(user):
    user.is_active = True
    user.is_email_verified = True
    user.is_super_user = True
    user.save()

def activate_free_trial(user):
    user.is_free_trial_activated = True
    user.save()


def update_base_subscription_plan_based_on_account_type(user):
    from subscription.models import SubscriptionPlan, UserSubscription
    if not user.stripe_customer_id:
        user.stripe_customer_id = Stripe_Service.get_or_create_stripe_customer(user)
        user.save()
    user_subscription = UserSubscription.objects.filter(user=user).first()
    if user.account_type == 1 :
        plan = SubscriptionPlan.objects.filter(pk=12).first()
    else:
        plan = SubscriptionPlan.objects.filter(pk=6).first()
    stripe_subscription = Stripe_Service.create_subscription(plan, user)
    user_subscription.stripe_id = stripe_subscription.id 
    user_subscription.save()
    allocate_brand_user_usages(user, plan)