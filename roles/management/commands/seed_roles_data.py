from django.core.management.base import BaseCommand


from roles.models import Permission, PermissionCategory

import json
import time


categories = [
    {
        "model": "roles.permissioncategory",
        "pk": 1,
        "fields": {
            "label": "xBrain",
            "description": "",
            "is_active": True,
            "group_type": "FAL",
        },
    },
    {
        "model": "roles.permissioncategory",
        "pk": 2,
        "fields": {
            "label": "Blocks (datasets)",
            "description": "",
            "is_active": True,
            "group_type": "FAL",
        },
    },
    {
        "model": "roles.permissioncategory",
        "pk": 3,
        "fields": {
            "label": "Meetings",
            "description": "",
            "is_active": True,
            "group_type": "FAL",
        },
    },
    {
        "model": "roles.permissioncategory",
        "pk": 4,
        "fields": {
            "label": "Tasks",
            "description": "",
            "is_active": True,
            "group_type": "FAL",
        },
    },
    {
        "model": "roles.permissioncategory",
        "pk": 5,
        "fields": {
            "label": "Brands and Locations",
            "description": "",
            "is_active": True,
            "group_type": "FAL",
        },
    },
    {
        "model": "roles.permissioncategory",
        "pk": 6,
        "fields": {
            "label": "Team management and Permissions",
            "description": "Affect the locations assigned to the user.",
            "is_active": True,
            "group_type": "FAL",
        },
    },
]


permissions = [
    {
        "model": "roles.permission",
        "pk": 1,
        "fields": {
            "component_key": "ua_answer",
            "label": "Unlimited access to answers",
            "description": "Receive detailed answers to any question about all brands and locations.",
            "is_active": True,
            "category_id": 1,
        },
    },
    {
        "model": "roles.permission",
        "pk": 2,
        "fields": {
            "component_key": "la_answer",
            "label": "Limited access to answers",
            "description": "Receive detailed answers to any question about specific locations.",
            "is_active": True,
            "category_id": 1,
        },
    },
    {
        "model": "roles.permission",
        "pk": 3,
        "fields": {
            "component_key": "ua_conversation_analytics",
            "label": "Unlimited access to conversation analytics",
            "description": "Access to analyze conversation data, derive insights, and evaluate performance metrics across all brands and locations. (Ensuring compliance with data privacy regulations.)",
            "is_active": True,
            "category_id": 1,
        },
    },
    {
        "model": "roles.permission",
        "pk": 4,
        "fields": {
            "component_key": "la_conversation_analytics",
            "label": "Limited access to conversation analytics",
            "description": "Access to analyze conversation data, derive insights, and evaluate performance metrics for assigned locations. (Ensuring compliance with data privacy regulations.)",
            "is_active": True,
            "category_id": 1,
        },
    },
    {
        "model": "roles.permission",
        "pk": 5,
        "fields": {
            "component_key": "pa_conversation",
            "label": "Personal access to conversation analytics",
            "description": "Users will have access to analyze their personal conversation data to derive insights and evaluate performance metrics.",
            "is_active": True,
            "category_id": 1,
        },
    },
    {
        "model": "roles.permission",
        "pk": 6,
        "fields": {
            "component_key": "ua_crud_block",
            "label": "Add, edit and delete blocks for all brands and loc",
            "description": "Can create new blocks, configure them, and assign them to any brand and location",
            "is_active": True,
            "category_id": 2,
        },
    },
    {
        "model": "roles.permission",
        "pk": 7,
        "fields": {
            "component_key": "la_crud_block",
            "label": "View and modify blocks for assigned locations.",
            "description": "",
            "is_active": True,
            "category_id": 2,
        },
    },
    {
        "model": "roles.permission",
        "pk": 8,
        "fields": {
            "component_key": "ua_block",
            "label": "Unlimited access to block's datasets",
            "description": "Receive detailed answers to any questions about all blocks across all brands and locations",
            "is_active": True,
            "category_id": 2,
        },
    },
    {
        "model": "roles.permission",
        "pk": 9,
        "fields": {
            "component_key": "la_block",
            "label": "Limited access to the block's datasets",
            "description": "Receive detailed answers to any questions about blocks in specific categories and locations",
            "is_active": True,
            "category_id": 2,
        },
    },
    {
        "model": "roles.permission",
        "pk": 10,
        "fields": {
            "component_key": "a_meeting",
            "label": "Active meeting feature",
            "description": "Users can schedule, host, edit and view meetings directly from their account.",
            "is_active": True,
            "category_id": 3,
        },
    },
    {
        "model": "roles.permission",
        "pk": 11,
        "fields": {
            "component_key": "la_meeting_analytics",
            "label": "Limited access to meeting analytics",
            "description": "Users will have access to analyze meeting data and evaluate performance metrics specifically for their assigned locations.",
            "is_active": True,
            "category_id": 3,
        },
    },
    {
        "model": "roles.permission",
        "pk": 12,
        "fields": {
            "component_key": "ua_meeting_analytics",
            "label": "Unlimited access to meeting analytics",
            "description": "Users will have access to analyze meeting data and evaluate performance metrics accross all brands and locations.",
            "is_active": True,
            "category_id": 3,
        },
    },
    {
        "model": "roles.permission",
        "pk": 13,
        "fields": {
            "component_key": "ua_task_analytics",
            "label": "Unlimited access to tasks analytics",
            "description": "Users will have access to analyze tasks data and evaluate performance metrics across all brands and locations.",
            "is_active": True,
            "category_id": 4,
        },
    },
    {
        "model": "roles.permission",
        "pk": 14,
        "fields": {
            "component_key": "la_task_analytics",
            "label": "Limited access to tasks analytics",
            "description": "Users will have access to analyze tasks data and evaluate performance metrics specifically for their assigned locations.",
            "is_active": True,
            "category_id": 4,
        },
    },
    {
        "model": "roles.permission",
        "pk": 15,
        "fields": {
            "component_key": "pa_meeting_crud_task",
            "label": "Manage meeting tasks for a specific meeting",
            "description": "User can assign, edit, and delete tasks related to their meetings",
            "is_active": True,
            "category_id": 4,
        },
    },
    {
        "model": "roles.permission",
        "pk": 16,
        "fields": {
            "component_key": "la_crud_task",
            "label": "Manage meeting tasks for location(s)",
            "description": "User can assign, edit and delete tasks related to all meetings, for assigned location (s)",
            "is_active": True,
            "category_id": 4,
        },
    },
    {
        "model": "roles.permission",
        "pk": 17,
        "fields": {
            "component_key": "ua_crud_brand",
            "label": "Add or remove Brand(s) and location(s)",
            "description": "User have access business information and can all or remove brands and locations.",
            "is_active": True,
            "category_id": 5,
        },
    },
    {
        "model": "roles.permission",
        "pk": 18,
        "fields": {
            "component_key": "ua_crud_team",
            "label": "Add, edit or delete team members",
            "description": "",
            "is_active": True,
            "category_id": 6,
        },
    },
    {
        "model": "roles.permission",
        "pk": 19,
        "fields": {
            "component_key": "set_role_user",
            "label": "Assign team member to role permission set",
            "description": "",
            "is_active": True,
            "category_id": 6,
        },
    },
    {
        "model": "roles.permission",
        "pk": 20,
        "fields": {
            "component_key": "ua_crud_role",
            "label": "Add, edit or delete role permission set",
            "description": "",
            "is_active": True,
            "category_id": 6,
        },
    },
]


def create_seed_category_data():
    category_instances = []
    for data in categories:
        category = PermissionCategory.objects.create(**data["fields"])
        category_instances.append(category)

    return category_instances


def create_seed_permission_data():

    for data in permissions:
        category_id = data["fields"].pop("category_id")
        category_label = categories[category_id - 1]["fields"]["label"]
        category = PermissionCategory.objects.get(label=category_label)
        permission = Permission.objects.create(**data["fields"], category=category)


class Command(BaseCommand):
    help = "Create seed data for roles app"

    def handle(self, *args, **kwargs):
        Permission.objects.all().delete()
        PermissionCategory.objects.all().delete()
        create_seed_category_data()
        create_seed_permission_data()
        self.stdout.write(self.style.SUCCESS("Successfully created seed data"))
