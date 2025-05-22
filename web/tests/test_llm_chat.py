from web.models.llm_chat import LLMChat
from web.tests.base_test import BaseTest

class LLMChatTestCase(BaseTest):
    def setUp(self):
        super().setUp()
        self.llm_chat = LLMChat.objects.create(user=self.user)
    
    def test_create_llmchat_with_valid_user_and_default_model(self):
        # Assertions
        self.assertEqual(self.llm_chat.user, self.user)
        self.assertEqual(self.llm_chat.model, "GPT-3.5")
        self.assertIsNotNone(self.llm_chat.created_at)
        self.assertIsNotNone(self.llm_chat.updated_at)

    def test_read_llmchat_instance(self):
        # Retrieve the instance and assert its properties
        read_llm_chat = LLMChat.objects.get(id=self.llm_chat.id)
        self.assertEqual(read_llm_chat.user, self.user)
        self.assertEqual(read_llm_chat.model, "GPT-3.5")
        self.assertIsNotNone(read_llm_chat.created_at)
        self.assertIsNotNone(read_llm_chat.updated_at)

    def test_update_llmchat_instance(self):
        # Update attributes
        self.llm_chat.model = "GPT-4"
        self.llm_chat.save()
        
        # Retrieve updated instance and assert changes
        updated_llm_chat = LLMChat.objects.get(id=self.llm_chat.id)
        self.assertEqual(updated_llm_chat.model, "GPT-4")
        self.assertEqual(updated_llm_chat.user, self.user)
        self.assertIsNotNone(updated_llm_chat.created_at)
        self.assertIsNotNone(updated_llm_chat.updated_at)

    def test_delete_llmchat_instance(self):
        # Delete the instance
        llm_chat_id = self.llm_chat.id
        self.llm_chat.delete()
        
        # Assert the instance no longer exists
        with self.assertRaises(LLMChat.DoesNotExist):
            LLMChat.objects.get(id=llm_chat_id)