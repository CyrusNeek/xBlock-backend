from web.models.assistant import Assistant
from web.tests.base_test import BaseTest

class AssistantTest(BaseTest):
    def test_create_assistant_with_required_fields(self):
        # Create an Assistant instance with all required fields
        assistant = Assistant.objects.create(
            user=self.user,
            assistant_id="assistant_123",
            model_type="gpt-3",
            vector_store_id="vector_123",
            purpose=Assistant.PURPOSE_DEFAULT
        )

        # Assertions to check if the instance is created correctly
        self.assertEqual(assistant.user, self.user)
        self.assertEqual(assistant.assistant_id, "assistant_123")
        self.assertEqual(assistant.model_type, "gpt-3")
        self.assertEqual(assistant.vector_store_id, "vector_123")
        self.assertEqual(assistant.purpose, Assistant.PURPOSE_DEFAULT)
        self.assertIsNotNone(assistant.created_at)
        self.assertIsNotNone(assistant.updated_at)

    def test_read_assistant_instance(self):
        # Create an Assistant instance
        assistant = Assistant.objects.create(
            user=self.user,
            assistant_id="assistant_456",
            model_type="gpt-4",
            vector_store_id="vector_456",
            purpose=Assistant.PURPOSE_DEFAULT
        )

        # Retrieve the instance and assert its attributes
        read_assistant = Assistant.objects.get(id=assistant.id)
        self.assertEqual(read_assistant.user, self.user)
        self.assertEqual(read_assistant.assistant_id, "assistant_456")
        self.assertEqual(read_assistant.model_type, "gpt-4")
        self.assertEqual(read_assistant.vector_store_id, "vector_456")
        self.assertEqual(read_assistant.purpose, Assistant.PURPOSE_DEFAULT)

    def test_update_assistant_instance(self):
        # Create an Assistant instance
        assistant = Assistant.objects.create(
            user=self.user,
            assistant_id="assistant_789",
            model_type="gpt-3",
            vector_store_id="vector_789",
            purpose=Assistant.PURPOSE_DEFAULT
        )

        # Update the instance
        assistant.assistant_id = "assistant_000"
        assistant.model_type = "gpt-3.5"
        assistant.vector_store_id = "vector_000"
        assistant.purpose = Assistant.PURPOSE_DEFAULT
        assistant.save()

        # Retrieve updated instance and assert changes
        updated_assistant = Assistant.objects.get(id=assistant.id)
        self.assertEqual(updated_assistant.assistant_id, "assistant_000")
        self.assertEqual(updated_assistant.model_type, "gpt-3.5")
        self.assertEqual(updated_assistant.vector_store_id, "vector_000")
        self.assertEqual(updated_assistant.purpose, Assistant.PURPOSE_DEFAULT)

    def test_delete_assistant_instance(self):
        # Create an Assistant instance
        assistant = Assistant.objects.create(
            user=self.user,
            assistant_id="assistant_delete",
            model_type="gpt-3",
            vector_store_id="vector_delete",
            purpose=Assistant.PURPOSE_DEFAULT
        )

        # Delete the instance
        assistant_id = assistant.id
        assistant.delete()

        # Assert the instance no longer exists
        with self.assertRaises(Assistant.DoesNotExist):
            Assistant.objects.get(id=assistant_id)