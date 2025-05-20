from web.models.openai_file import OpenAIFile
from web.tests.base_test import BaseTest
from django.utils import timezone

class OpenAIFileTestCase(BaseTest):       
    def setUp(self):
        super().setUp()
        self.openai_file = OpenAIFile(
            file_name="test_file.txt",
            file_id="12345",
            unit=self.unit,
            model_name=OpenAIFile.CategoryChoices.TOCK,
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
        
    def test_create_openai_file_with_valid_data(self):
        # Assertions
        self.assertEqual(self.openai_file.file_name, "test_file.txt")
        self.assertEqual(self.openai_file.file_id, "12345")
        self.assertEqual(self.openai_file.unit, self.unit)
        self.assertEqual(self.openai_file.model_name, OpenAIFile.CategoryChoices.TOCK)
        self.assertEqual(str(self.openai_file), "Test Unit - test_file.txt")

    def test_retrieve_openaifile_instance(self):
        # Access attributes and assert
        self.assertEqual(self.openai_file.file_name, "test_file.txt")
        self.assertEqual(self.openai_file.file_id, "12345")
        self.assertEqual(self.openai_file.unit, self.unit)
        self.assertEqual(self.openai_file.model_name, OpenAIFile.CategoryChoices.TOCK)

        # Updating an OpenAIFile instance and saving changes
    def test_update_openaifile_instance(self):
        # Update attributes
        self.openai_file.file_name = "Updated File"
        self.openai_file.file_id = "456"
        self.openai_file.model_name = OpenAIFile.CategoryChoices.RESY_RESERVATION
        self.openai_file.save()
        # Retrieve updated instance and assert changes
        updated_openai_file = OpenAIFile.objects.get(id=self.openai_file.id)
        self.assertEqual(updated_openai_file.file_name, "Updated File")
        self.assertEqual(updated_openai_file.file_id, "456")
        self.assertEqual(updated_openai_file.model_name, OpenAIFile.CategoryChoices.RESY_RESERVATION)