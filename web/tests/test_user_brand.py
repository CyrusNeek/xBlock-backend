from web.models.brand import Brand
from web.models.user_brand import UserBrand
from web.tests.base_test import BaseTest

class UserBrandTestCase(BaseTest):       
    def setUp(self):
        super().setUp()
        self.user_brand = UserBrand.objects.create(user=self.user, brand=self.brand)
        
        
    def test_create_userbrand_with_valid_user_and_brand(self):
        # Assertions
        self.assertEqual(self.user_brand.user, self.user)
        self.assertEqual(self.user_brand.brand, self.brand)
        # self.assertEqual(str(self.user_brand), f"{self.brand.name} {self.user.username}")

    def test_update_userbrand(self):
        # Update the Brand instance
        new_brand = Brand.objects.create(name="New Brand")
        self.user_brand.brand = new_brand
        self.user_brand.save()

        # Assertions
        self.assertEqual(self.user_brand.brand, new_brand)
        # self.assertEqual(str(self.user_brand), f"{new_brand.name} {self.user.username}")

    def test_delete_userbrand(self):
        # Delete the UserBrand instance
        user_brand_id = self.user_brand.id
        self.user_brand.delete()

        # Assertions
        with self.assertRaises(UserBrand.DoesNotExist):
            UserBrand.objects.get(id=user_brand_id)