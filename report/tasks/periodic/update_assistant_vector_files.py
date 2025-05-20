from celery import shared_task
from django.db.models import Q
from report.tasks.periodic.openai_helper import get_or_create_vector_store_id
from roles.models import Role
from web.models.assistant import Assistant
from web.models import Unit, BlockCategory, OpenAIFile
from roles.constants import (
    UNLIMITED_MEETING_ACCESS,
    LIMITED_MEETING_ACCESS,
    UNLIMITED_TASK_ANALYTICS_ACCESS,
    LIMITED_TASK_ANALYTICS_ACCESS,
    UNLIMITED_ANSWER_ACCESS,
)

from openai import OpenAI
from django.conf import settings

from web.models.user import User
from web.tasks.unit_file.task_unitfile_creation import check_permission


client = OpenAI(api_key=settings.OPENAI_API_KEY)


def is_authorized_for_file(user: User, file: OpenAIFile):
    if file.model_name in ["resy", "tock", "unit-file", "toast", "events"]:
        if not file.block_category:
            return True
        if file.block_category in BlockCategory.objects.accessible_by_user(user):
            return True

        return False

    if file.model_name == "meeting":
        return user.has_permission(UNLIMITED_MEETING_ACCESS, LIMITED_MEETING_ACCESS)

    if file.model_name == "task":
        return user.has_permission(
            UNLIMITED_TASK_ANALYTICS_ACCESS, LIMITED_TASK_ANALYTICS_ACCESS
        )

    return True

@shared_task
def update_assistant_vector_files(assistant_pk: int):
    return
    try:
        assistant = Assistant.objects.get(pk=assistant_pk)
    except Assistant.DoesNotExist:
        return
    user = assistant.user
    from django.db.models import Q
    units = Unit.objects.filter(Q(users=user) | Q(user_set=user))

    unit_pks = units.values_list("id", flat=True)

    block_categories = BlockCategory.objects.accessible_by_user(user)

    files = OpenAIFile.objects.filter(
        ~Q(pk__in=assistant.files.all()),
        Q(block_category__in=block_categories) | Q(unit__in=units),
    )

    assigned_files = assistant.files.all()

    if not assistant.vector_store_id:
        get_or_create_vector_store_id(assistant)

    for file in assigned_files:
        if file.unit.pk not in unit_pks or (
            not check_permission(user, file.block_category)
        ):
            try:
                client.beta.vector_stores.files.delete(
                    file_id=file.file_id, vector_store_id=assistant.vector_store_id
                )
            except Exception as e:
                pass
            assistant.files.remove(file)

    for file in files.all():
        if not is_authorized_for_file(user, file):
            continue
        try:
            client.beta.vector_stores.files.create(
                file_id=file.file_id,
                vector_store_id=assistant.vector_store_id,
            )

            assistant.files.add(file)
        except Exception as e:
            pass

    assistant.save()


@shared_task
def evaluate_role_update(role_pk: int):
    try:
        role = Role.objects.get(pk=role_pk)
    except Role.DoesNotExist:
        return
    for user in role.users.all():
        if not user.assistant_set.exists():
            continue

        if user.assistant_set.exists():
            update_assistant_vector_files(user.assistant_set.first().pk)
