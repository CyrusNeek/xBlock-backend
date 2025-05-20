from web.models import BlockCategory
from web.tests.base_test import BaseTest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

class BlockCategoryTestCase(BaseTest):
    def setUp(self):
        super().setUp()
        self.api_client = APIClient()
        self.block_category = BlockCategory.objects.create(
            name="Test Category",
            color=BlockCategory.Color.RED,
            description="This is a test description"
        )
        self.block_category.units.add(self.unit)
    
    def test_create_block_category_with_valid_data(self):
        # Assertions to check if the instance is created correctly
        self.assertEqual(self.block_category.name, "Test Category")
        self.assertEqual(self.block_category.description, "This is a test description")

    def test_read_block_category_instance(self):
        # Retrieve the instance and assert its attributes
        read_block_category = BlockCategory.objects.get(id=self.block_category.id)
        self.assertEqual(read_block_category.name, "Test Category")
        self.assertEqual(read_block_category.description, "Another description")

    def test_update_block_category_instance(self):
        # Update the instance
        self.block_category.name = "Updated Category"
        self.block_category.color = BlockCategory.Color.RED
        self.block_category.description = "Updated description"
        self.block_category.save()

        # Retrieve updated instance and assert changes
        updated_block_category = BlockCategory.objects.get(id=self.block_category.id)
        self.assertEqual(updated_block_category.name, "Updated Category")
        self.assertEqual(updated_block_category.description, "Updated description")
            
    def test_create_block_category(self):
        self.api_client.force_authenticate(user=self.user)
        url = reverse('blockcategory-list')
        data = {
            "name": "New Category",
            "color": "Blue",
            "units": [self.unit.id],
            "description": "A test block category"
        }
        response = self.api_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BlockCategory.objects.count(), 2)
        self.assertEqual(BlockCategory.objects.get(id=response.data['id']).name, "New Category")

    def test_read_block_category(self):
        self.api_client.force_authenticate(user=self.user)
        url = reverse('blockcategory-detail', args=[self.block_category.id])
        response = self.api_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.block_category.name)

    def test_update_block_category(self):
        self.api_client.force_authenticate(user=self.user)
        url = reverse('blockcategory-detail', args=[self.block_category.id])
        data = {
            "name": "Updated Category",
            "color": "Green"
        }
        response = self.api_client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.block_category.refresh_from_db()
        self.assertEqual(self.block_category.name, "Updated Category")
        self.assertEqual(self.block_category.color, "Green")

    def test_delete_block_category(self):
        self.api_client.force_authenticate(user=self.user)
        url = reverse('blockcategory-detail', args=[self.block_category.id])
        response = self.api_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(BlockCategory.objects.count(), 0)
        
        
    def test_delete_block_category_instance(self):
        # Delete the instance
        block_category_id = self.block_category.id
        self.block_category.delete()

        # Assert the instance no longer exists
        with self.assertRaises(BlockCategory.DoesNotExist):
            BlockCategory.objects.get(id=block_category_id)