from web.models.group import Group
from web.tests.base_test import BaseTest

class GroupTestCase(BaseTest):
    def test_create_group_instance(self):
        # Assertions
        self.assertEqual(self.group.name, "Test Group")
        self.assertEqual(self.group.unit, self.unit)
        self.assertEqual(self.group.description, "A test group")
        self.assertEqual(self.group.permission_level, 0)
        self.assertEqual(list(self.group.users.all()), [self.user, self.user2])

    def test_read_group_instance(self):
        # Retrieve the instance and assert its properties
        read_group = Group.objects.get(id=self.group.id)
        self.assertEqual(read_group.name, "Test Group")
        self.assertEqual(read_group.unit, self.unit)
        self.assertEqual(read_group.description, "A test group")
        self.assertEqual(read_group.permission_level, 0)
        self.assertEqual(list(read_group.users.all()), [self.user, self.user2])

    def test_update_group_instance(self):
        # Update attributes
        self.group.name = "Updated Test Group"
        self.group.permission_level = 1
        self.group.description = "An updated test group"
        self.group.save()
        
        # Retrieve updated instance and assert changes
        updated_group = Group.objects.get(id=self.group.id)
        self.assertEqual(updated_group.name, "Updated Test Group")
        self.assertEqual(updated_group.permission_level, 1)
        self.assertEqual(updated_group.description, "An updated test group")
        self.assertEqual(list(updated_group.users.all()), [self.user, self.user2])

    def test_delete_group_instance(self):
        # Delete the instance
        group_id = self.group.id
        self.group.delete()
        
        # Assert the instance no longer exists
        with self.assertRaises(Group.DoesNotExist):
            Group.objects.get(id=group_id)

    def test_retrieve_group_attributes(self):
        # Test
        self.assertEqual(self.group.name, "Test Group")
        self.assertEqual(self.group.unit, self.unit)
        self.assertEqual(list(self.group.users.all()), [self.user, self.user2])
        self.assertEqual(self.group.permission_level, 0)
        self.assertEqual(self.group.description, "A test group")