from web.models.meeting import Meeting
from web.tests.base_test import BaseTest

class MeetingTestCase(BaseTest):
    def setUp(self):
        super().setUp()
        self.meeting = Meeting.objects.create(
            length=60,
            key_points="Discussed project requirements",
            unit=self.unit,
            name="Project Kickoff",
            recording_file_url="http://example.com/recording.mp4",
            created_by=self.user
        )
        self.meeting.participants.add(self.user, self.user2)
            
    def test_create_meeting_instance(self):
        # Retrieve the instance and assert its creation
        created_meeting = Meeting.objects.get(id=self.meeting.id)
        self.assertEqual(created_meeting.length, 60)
        self.assertEqual(created_meeting.key_points, "Discussed project requirements")
        self.assertEqual(created_meeting.unit, self.unit)
        self.assertEqual(created_meeting.name, "Project Kickoff")
        self.assertEqual(created_meeting.recording_file_url, "http://example.com/recording.mp4")
        self.assertEqual(created_meeting.created_by, self.user)
        self.assertEqual(created_meeting.participants.count(), 2)

    def test_read_meeting_instance(self):
        # Retrieve the instance and assert its properties
        read_meeting = Meeting.objects.get(id=self.meeting.id)
        self.assertEqual(read_meeting.length, 60)
        self.assertEqual(read_meeting.key_points, "Discussed project requirements")
        self.assertEqual(read_meeting.unit, self.unit)
        self.assertEqual(read_meeting.name, "Project Kickoff")
        self.assertEqual(read_meeting.recording_file_url, "http://example.com/recording.mp4")
        self.assertEqual(read_meeting.created_by, self.user)
        self.assertEqual(read_meeting.participants.count(), 2)
    
    def test_update_meeting_instance(self):
        # Update attributes
        self.meeting.length = 90
        self.meeting.key_points = "Discussed new project timeline"
        self.meeting.save()
        
        # Retrieve updated instance and assert changes
        updated_meeting = Meeting.objects.get(id=self.meeting.id)
        self.assertEqual(updated_meeting.length, 90)
        self.assertEqual(updated_meeting.key_points, "Discussed new project timeline")
    
    def test_delete_meeting_instance(self):
        # Delete the instance
        meeting_id = self.meeting.id
        self.meeting.delete()
        
        # Assert the instance no longer exists
        with self.assertRaises(Meeting.DoesNotExist):
            Meeting.objects.get(id=meeting_id)