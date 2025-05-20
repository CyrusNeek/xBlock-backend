from celery import shared_task
import logging
from django.shortcuts import get_object_or_404
from django.db import transaction
from web.models import User, LLMChat
from vtk.models import XClassmate
from accounting.models import Team
from employee.models import (
    Employee,
    EmploymentDetail,
    PersonalInformation,
    VoiceInteraction,
    KnowledgeBaseContribution,
    Conversation,
    Department,
    Manager,
)

logger = logging.getLogger(__name__)


def create_employee_objects():
    try:
        users = User.objects.filter(new_models=False)

        for user in users:
            user_unit = (
                user.unit
                if user.unit
                else user.units.first() if user.units.exists() else None
            )

            Employee.objects.update_or_create(
                first_name=user.first_name or None,
                last_name=user.last_name or None,
                full_name=user.full_name or f"{user.first_name} {user.last_name}",
                preferred_name=user.display_name,
                email=user.email or user.username,
                phone_number=user.phone_number or None,
                employment_status="active",
                employment_start_date=user.date_joined,
                location=user_unit.name if user_unit else None,
            )

            user.new_models = True
            user.save(update_fields=["new_models"])

        logger.info(f"Processed {len(users)} employee objects.")
    except Exception as e:
        logger.error(f"Error in create_employee_objects: {str(e)}")


def create_user_voice_interaction():
    try:
        chats = LLMChat.objects.filter(new_models=False).select_related("user")
        employees = {
            emp.email: emp
            for emp in Employee.objects.filter(
                email__in=[chat.user.username or chat.user.email for chat in chats]
            )
        }

        for chat in chats:
            emp = employees.get(chat.user.username)
            if emp:
                Conversation.objects.update_or_create(
                    employee=emp,
                    conversation_date=chat.created_at.date(),
                    conversation_time=chat.created_at.time(),
                    conversation_type=Conversation.CHAT,
                    content=chat.messages,
                    language="English",
                )
            chat.new_models = True

        with transaction.atomic():
            LLMChat.objects.bulk_update(chats, ["new_models"])

        logger.info(f"Processed {len(chats)} chats.")
    except Exception as e:
        logger.error(f"Error in create_user_voice_interaction: {str(e)}")


def create_knowledge_base_contribution_objects():
    try:
        items = XClassmate.objects.filter(
            diarization_id__isnull=False, new_models=False
        )
        for item in items:
            user = User.objects.get(pk=item.created_by.pk)
            emp = Employee.objects.get(email=user.username or user.email)

            KnowledgeBaseContribution.objects.update_or_create(
                employee=emp,
                contribution_date=item.created_at,
                content_type=KnowledgeBaseContribution.TALK,
                title=f"{item.name} | Speech To Knowledge",
            )

            item.new_models = True
            item.save()

        logger.info(f"Processed {len(items)} knowledge base contributions.")
    except Exception as e:
        logger.error(f"Error in create_knowledge_base_contribution_objects: {str(e)}")


def create_manager_objects():
    try:
        team_managers = (
            User.objects.filter(team__team_manager__isnull=False)
            .distinct()
            .select_related("unit", "team")
        )
        employees = {
            emp.email: emp
            for emp in Employee.objects.filter(
                email__in=[tm.username or tm.email for tm in team_managers]
            )
        }

        for user in team_managers:
            user_unit = user.unit or user.units.first() if user.units.exists() else None
            employee = employees.get(user.username)

            manager, _ = Manager.objects.get_or_create(employee=employee)

            if user.team:
                team = user.team
                parent_team = team.parent if team.parent else None

                if parent_team:
                    parent_user = parent_team.team_manager
                    parent_emp = employees.get(parent_user.username)
                    parent_manager, _ = Manager.objects.get_or_create(
                        employee=parent_emp
                    )

                    Department.objects.get_or_create(
                        department_name=parent_team.name,
                        description=parent_team.description,
                        manager=parent_manager,
                        location=user_unit.name if user_unit else None,
                    )

                department = Department.objects.get_or_create(
                    department_name=team.name,
                    description=team.description,
                    parent=parent_team if parent_team else None,
                    manager=manager,
                    location=user_unit.name if user_unit else None,
                )

                employee.department = department
                employee.save()

        logger.info(f"Processed {len(team_managers)} team managers.")
    except Exception as e:
        logger.error(f"Error in create_manager_objects: {str(e)}")


@shared_task
def create_employee_app_data():
    create_employee_objects()
    create_user_voice_interaction()
    create_knowledge_base_contribution_objects()
    create_manager_objects()
