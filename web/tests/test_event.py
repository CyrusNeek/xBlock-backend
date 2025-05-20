from web.models.event import Event
from web.tests.base_test import BaseTest
from django.utils import timezone

class EventTestCase(BaseTest):
    def setUp(self):
        super().setUp()
        self.event = Event.objects.create(
            name="Sample Event",
            link="http://example.com",
            date=timezone.now().date(),
            start_time=timezone.now().time(),
            end_time=timezone.now().time()
        )
        
    
    
    def test_create_event_with_valid_data(self):
        self.assertEqual(self.event.name, "Sample Event")
        self.assertEqual(self.event.link, "http://example.com")
        self.assertEqual(self.event.date, timezone.now().date())
        self.assertIsNotNone(self.event.start_time)
        self.assertIsNotNone(self.event.end_time)
        self.assertIsNotNone(self.event.created_at)

    def test_read_event_instance(self):
        read_event = Event.objects.get(id=self.event.id)
        self.assertEqual(read_event.name, "Sample Event")
        self.assertEqual(read_event.link, "http://example.com")
        self.assertEqual(read_event.date, timezone.now().date())
        self.assertIsNotNone(read_event.start_time)
        self.assertIsNotNone(read_event.end_time)
        self.assertIsNotNone(read_event.created_at)

    def test_update_event_instance(self):
        self.event.name = "Updated Event"
        self.event.link = "http://updatedexample.com"
        self.event.save()

        updated_event = Event.objects.get(id=self.event.id)
        self.assertEqual(updated_event.name, "Updated Event")
        self.assertEqual(updated_event.link, "http://updatedexample.com")
        self.assertEqual(updated_event.date, timezone.now().date())
        self.assertIsNotNone(updated_event.start_time)
        self.assertIsNotNone(updated_event.end_time)
        self.assertIsNotNone(updated_event.created_at)

    def test_delete_event_instance(self):
        event_id = self.event.id
        self.event.delete()

        with self.assertRaises(Event.DoesNotExist):
            Event.objects.get(id=event_id)