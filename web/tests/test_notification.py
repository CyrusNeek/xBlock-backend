from web.models.notification import Notification
from web.tests.base_test import BaseTest

class NotificationTestCase(BaseTest):       
    def setUp(self):
        super().setUp()
        self.notification = Notification.objects.create(user=self.user, message="Test Message")
        
    def test_create_notification_instance(self):
        # Retrieve the instance and assert its creation
        created_notification = Notification.objects.get(id=self.notification.id)
        self.assertEqual(created_notification.message, "Test Message")
        self.assertFalse(created_notification.is_read)

    def test_read_notification_instance(self):
        # Retrieve the instance and assert its properties
        read_notification = Notification.objects.get(id=self.notification.id)
        self.assertEqual(read_notification.message, "Test Message")
        self.assertFalse(read_notification.is_read)

    def test_update_notification_instance(self):
        # Update attributes
        self.notification.message = "Updated Message"
        self.notification.is_read = True
        self.notification.save()
        # Retrieve updated instance and assert changes
        updated_notification = Notification.objects.get(id=self.notification.id)
        self.assertEqual(updated_notification.message, "Updated Message")
        self.assertTrue(updated_notification.is_read)

    def test_delete_notification_instance(self):
        # Delete the instance
        notification_id = self.notification.id
        self.notification.delete()
        # Assert the instance no longer exists
        with self.assertRaises(Notification.DoesNotExist):
            Notification.objects.get(id=notification_id)