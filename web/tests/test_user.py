from unittest.mock import patch
from web.models.user import User
from web.tests.base_test import BaseTest

class UserTestCase(BaseTest):       
    def setUp(self):
        super().setUp()
        
        
    def test_create_user(self):
        self.assertEqual(self.user.username, self.user_data['username'])
        self.assertEqual(self.user.first_name, self.user_data['first_name'])
        self.assertEqual(self.user.last_name, self.user_data['last_name'])
        self.assertEqual(self.user.email, self.user_data['email'])

    def test_update_user(self):
        new_data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com',
        }
        for key, value in new_data.items():
            setattr(self.user, key, value)
        self.user.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, new_data['first_name'])
        self.assertEqual(self.user.last_name, new_data['last_name'])
        self.assertEqual(self.user.email, new_data['email'])

    # User with limited permission can access only specific units assigned to them
    def test_user_with_limited_permission_access(self):
        self.assertEqual(len(self.user.units.all()), 0)
        self.user.units.set([self.unit])

        with patch('roles.permissions.UserPermission.check_user_permission') as mock_check_user_permission:
            mock_check_user_permission.return_value = True  # Simulating limited permission
            self.assertIn(self.unit, self.user.units.all())
            self.assertEqual(len(self.user.units.all()), 1)
            
    def test_delete_user(self):
        self.user.delete()
        self.assertFalse(User.objects.filter(username=self.user_data['username']).exists())