from django.db import models
from .meeting import Meeting
from .unit import Unit
from django.db.models import Q
from roles.permissions import UserPermission
from roles.constants import (
    PARTICIPATED_MEETING_TASK_CRUD_ACCESS,
    LIMITED_TASK_MEETING_CRUD_ACCESS,
)
from web.models.meeting import Meeting


class TaskManager(models.Manager):
    def accessible_by_user(self, user):
        unit_meetings_tasks = UserPermission.check_user_permission(
            user, LIMITED_TASK_MEETING_CRUD_ACCESS
        )
        specific_meetings_tasks = UserPermission.check_user_permission(
            user, PARTICIPATED_MEETING_TASK_CRUD_ACCESS
        )

        query = Q()

        if unit_meetings_tasks:
            units = list(user.units.all())
            query |= Q(unit__in=units)

        if specific_meetings_tasks:
            meetings = Meeting.objects.filter(participants=user)
            query |= Q(meeting__in=meetings)

        # Always include tasks assigned to or created by the user
        query |= Q(assignee=user) | Q(created_by=user)

        tasks = self.get_queryset().filter(query).distinct().order_by("-created_at")

        return tasks


class Task(models.Model):
    class Status(models.TextChoices):
        BACKLOG = "Backlog"
        TODO = "Todo"
        IN_PROGRESS = "In Progress"
        DONE = "Done"
        CANCELED = "Canceled"

    objects = TaskManager()

    created_by = models.ForeignKey(
        "User", on_delete=models.SET_NULL, null=True, related_name="assigned_tasks"
    )
    assignee = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks_assigned",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.BACKLOG,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    meeting = models.ForeignKey(
        Meeting, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks"
    )
    xclassmate = models.ForeignKey(
        'vtk.XClassmate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )
    unit = models.ForeignKey(
        Unit, on_delete=models.CASCADE, related_name="tasks", blank=True, null=True
    )
    due_date = models.DateTimeField(null=True, blank=True)
    assigned_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.description
