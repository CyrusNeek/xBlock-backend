from web.models.unit_file import UnitFile
from web.tests.base_test import BaseTest

class UnitFileTestCase(BaseTest):       
    def setUp(self):
        super().setUp()
        self.unit_file = UnitFile.objects.create(
            user=self.user,
            file_url="https://example.com/file.pdf",
            file_description="Test file description",
            file_name="file.pdf",
            uploaded=True,
            file_size=1024.0,
            file_type="pdf",
            openai_file_id="12345"
        )
        
    def test_unitfile_creation_with_valid_data(self):
        
        self.assertEqual(self.unit_file.user, self.user)
        self.assertEqual(self.unit_file.file_url, "https://example.com/file.pdf")
        self.assertEqual(self.unit_file.file_description, "Test file description")
        self.assertEqual(self.unit_file.file_name, "file.pdf")
        self.assertTrue(self.unit_file.uploaded)
        self.assertEqual(self.unit_file.file_size, 1024.0)
        self.assertEqual(self.unit_file.file_type, "pdf")
        self.assertEqual(self.unit_file.openai_file_id, "12345")
        
    def test_unitfile_deletion(self):
        # Ensure the UnitFile instance exists in the database
        self.assertTrue(UnitFile.objects.filter(id=self.unit_file.id).exists())

        # Delete the UnitFile instance
        self.unit_file.delete()

        # Check that the UnitFile instance no longer exists in the database
        self.assertFalse(UnitFile.objects.filter(id=self.unit_file.id).exists())