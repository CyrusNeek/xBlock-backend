from unittest.mock import patch
from web.models.meeting import Meeting
from web.models.tasks import Task
from web.tests.base_test import BaseTest
from django.utils import timezone

class TaskTestCase(BaseTest):       
    def setUp(self):
        super().setUp()
        self.meeting = Meeting.objects.create(name="Test Meeting",length=200)
        
    def test_task_creation_with_valid_data_succeeds(self):
        # Mocking the UserPermission.check_user_permission method
        with patch('roles.permissions.UserPermission.check_user_permission') as mock_check_user_permission:
            mock_check_user_permission.return_value = True

            # Exercise
            tasks = Task.objects.accessible_by_user(self.user)

            # Assert
            self.assertEqual(len(tasks), 0)  # Assuming no tasks are created yet

    def test_task_creation_all_fields_populated(self):
        # Exercise
        task = Task.objects.create(
            description="Task with all fields",
            created_by=self.user,
            assignee=self.user,
            status=Task.Status.IN_PROGRESS,
            meeting=self.meeting,
            unit=self.unit,
            due_date=timezone.now(),
            assigned_date=timezone.now()
        )
    
        # Assert
        self.assertEqual(task.description, "Task with all fields")
        self.assertEqual(task.created_by, self.user)
        self.assertEqual(task.assignee, self.user)
        self.assertEqual(task.status, Task.Status.IN_PROGRESS)
        self.assertEqual(task.meeting, self.meeting)
        self.assertEqual(task.unit, self.unit)
        self.assertIsNotNone(task.due_date)
        self.assertIsNotNone(task.assigned_date)
        
    def test_delete_task(self):
        task = Task.objects.create(
            description="Task to be deleted",
            created_by=self.user,
            assignee=self.user,
            status=Task.Status.CANCELED,
            meeting=self.meeting,
            unit=self.unit,
            due_date=timezone.now(),
            assigned_date=timezone.now(),
        )
    
        # Exercise
        task_id = task.id
        task.delete()
    
        # Assert
        with self.assertRaises(Task.DoesNotExist):
            Task.objects.get(id=task_id)