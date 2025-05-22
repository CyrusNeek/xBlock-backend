from roles.constants import (
    LIMITED_ACCESS_TO_CONVERSATION_ANALYTICS,
    UNLIMITED_ACCESS_TO_CONVERSATION_ANALYTICS,
)
from roles.permissions import UserPermission
from web.models import User, Unit
from web.models.block_category import BlockCategory


def filter_collection_blocks_permissions(user: User, resources):
    accessible_blocks = BlockCategory.objects.accessible_by_user(user).values_list(
        "id", flat=True
    )

    accessible_units = Unit.objects.accessible_by_user(user).values_list(
        "id", flat=True
    )

    result = []

    for row in resources:
        properties = row.properties
        if UserPermission.check_user_permission(user, UNLIMITED_ACCESS_TO_CONVERSATION_ANALYTICS):
            pass

        elif UserPermission.check_user_permission(user, LIMITED_ACCESS_TO_CONVERSATION_ANALYTICS):
            # properties = {"error": "Forbidden user permission restricts access to this resource"}
            
            if row.get("block_category"):
                if row["block_category"] not in accessible_blocks:
                    properties = {"error": "Forbidden user permission restricts access to this resource"}

            elif row.get("unit") and row['unit'] not in accessible_units:
                properties = {"error": "Forbidden user permission restricts access to this resource"}
        else:
            properties = {"error": "Forbidden user permission restricts access to this resource"}

        result.append(properties)

    return result


def filter_report_users_permissions(user: User, resources):
    brands = user.brands.values_list("id", flat=True)

    result = []

    for row in resources:
        properties = row.properties
        if row["brand"] not in brands:
            properties = {
                "error": "Forbidden user permission restricts access to this resource"
            }

        result.append(properties)

    return result
