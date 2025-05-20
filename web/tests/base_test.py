

from django.test import TestCase

from django.db.models.signals import post_save

from web.models.brand import Brand
from web.models.group import Group
from web.models.unit import Unit
from web.models.user import User
from web.signals.user_signals import signal_user_creation

class BaseTest(TestCase):
    def setUp(self):
        # Disconnect the signal
        post_save.disconnect(signal_user_creation, sender=User)
        
        
        self.brand = Brand.objects.create(name="Test Brand")
        self.unit = Unit.objects.create(name="Test Unit", brand=self.brand)
        self.user_data = {
            'username': 'testuser',
            'password': 'testpassword',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'testuser@example.com',
        }
        self.user = User.objects.create(**self.user_data)
        user2_data = self.user_data.copy()
        user2_data['username']="testuser2"
        user2_data['password']="testpass2"
        self.user2 = User.objects.create_user(**user2_data)
        self.group = Group.objects.create(name="Test Group", unit=self.unit, description="A test group")
        self.group.users.add(self.user, self.user2)
        
        
    def tearDown(self):
        # Reconnect the signal
        post_save.connect(signal_user_creation, sender=User)