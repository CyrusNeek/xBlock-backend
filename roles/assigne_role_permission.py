from roles.models import Permission, Role
from subscription.models.user_subscription import UserSubscription
from web.models import brand_owner
from roles.constants import (
    ACTIVE_MEETING_ACCESS,
    UNLIMITED_ANSWER_ACCESS,
    LIMITED_ANSWER_ACCESS,
    XCLASSMATE_ACCESS,
    UNLIMITED_CRUD_BLOCK_ACCESS,
)
from web.models.user import User
from web.utils import PushNotification
import logging
logger = logging.getLogger(__name__)


def get_true_variables(meeting, classmate, token, upload):
    # Create a dictionary with variable names and values
    variables = {
        'meeting': meeting,
        'classmate': classmate,
        'token': token,
        'upload': upload
    }
    # Return the names of variables that are True
    return [key for key, value in variables.items() if value]


def assigne_role_permission(user_id: int, role_id: int):
    try:
        notif = PushNotification()
        user = User.objects.get(pk=user_id)

        plan = UserSubscription.objects.get(
            brand_owner=user.affiliation, status=UserSubscription.ACTIVE
        )

        role = Role.objects.get(pk=role_id)

        role_permissions = list(
            role.permissions.values_list("component_key", flat=True)
        )

        xbrain_permissions = [
            LIMITED_ANSWER_ACCESS,
            UNLIMITED_ANSWER_ACCESS,
        ]

        classmate_permissions = [XCLASSMATE_ACCESS]
        meeting_permissions = [ACTIVE_MEETING_ACCESS]
        upload_permission = [UNLIMITED_CRUD_BLOCK_ACCESS]
        meeting = False
        classmate = False
        token = False
        upload = False

        if any(permission in role_permissions for permission in xbrain_permissions):
            if plan.token_user_limit <= 0:
                notif.send_notification(
                    user=user,
                    title=f"Failed to assigne role {role.label}",
                    body=f"Your current subscription plan has reached its user limit. To accommodate additional users, please upgrade your plan or remove unnecessary permissions or users.",
                )
                return False
            else:
                token = True

        if any(permission in role_permissions for permission in meeting_permissions):
            if plan.meeting_user_limit <= 0:
                notif.send_notification(
                    user=user,
                    title=f"Failed to assigne role {role.label}",
                    body=f"Your current subscription plan has reached its user limit. To accommodate additional users, please upgrade your plan or remove unnecessary permissions or users.",
                )
                return False
            else:
                meeting = True

        if any(permission in role_permissions for permission in classmate_permissions):
            if plan.classmate_user_limit <= 0:
                notif.send_notification(
                    user=user,
                    title=f"Failed to assigne role {role.label}",
                    body=f"Your current subscription plan has reached its user limit. To accommodate additional users, please upgrade your plan or remove unnecessary permissions or users.",
                )
                return False
            else:
                classmate = True
                
        if any(permission in role_permissions for permission in upload_permission):
            if plan.upload_user_limit <= 0:
                notif.send_notification(
                    user=user,
                    title=f"Failed to assigne role {role.label}",
                    body=f"Your current subscription plan has reached its user limit. To accommodate additional users, please upgrade your plan or remove unnecessary permissions or users.",
                )
                return False
            else:
                upload = True

        return get_true_variables(meeting=meeting, token=token, classmate=classmate, upload=upload)
    except Exception as err:
            logger.error(f"An unexpected error occurred: {err}")
            raise
