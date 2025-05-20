from celery import shared_task
from web.models import Task, Meeting, User
from xmeeting.models import ActionItem, XMeeting, Employee
import logging


logger = logging.getLogger(__name__)

@shared_task
def create_action_item_xmeeting():
    tasks = Task.objects.select_related('meeting', 'assignee').all()

    for task in tasks:
        if task.meeting and task.assignee:
            meeting = task.meeting
            user = User.objects.get(pk=task.assignee)

            try:
                xmeeting, _ = XMeeting.objects.get(
                    xmeeting_title=meeting.name,
                    xmeeting_date=meeting.created_at.date(),
                    defaults={
                        'duration_minutes': meeting.length // 60,
                    }
                )
            except XMeeting.DoesNotExist:
                logger.error(f"XMeeting not found for meeting {meeting.pk}")
                continue

            status = task.status

            if status == Task.Status.TODO:
                action_item_status = ActionItem.STATUS_PENDING
            if status == Task.Status.BACKLOG:
                action_item_status = ActionItem.STATUS_OVERDUE
            if status == Task.Status.IN_PROGRESS:
                action_item_status = ActionItem.STATUS_IN_PROGRESS
            if status == Task.Status.CANCELED:
                action_item_status = ActionItem.STATUS_OVERDUE
            else:
                action_item_status = None

            employee, _ = Employee.objects.get_or_create(
                first_name=user.first_name,
                last_name=user.last_name,
                full_name=user.full_name,
                email=user.email,
            )

            ActionItem.objects.create(
                xmeeting=xmeeting,
                description=task.description,
                assigned_to=employee,
                due_date=task.due_date,
                status=action_item_status,
            )

            logger.info(f"ActionItem created for task {task.pk} and xmeeting {xmeeting.pk}")
