from web.models.brand_owner import BrandOwner
from web.tests.base_test import BaseTest

class BrandOwnerTestCase(BaseTest):
    def test_create_brandowner_with_all_fields(self):
        brand_owner = BrandOwner.objects.create(
            name="Test Brand",
            description="This is a test brand owner.",
            public_business_name="Test Public Name",
            email="test@example.com",
            phone_number="1234567890",
            account_name="testaccount",
            zip_code="12345",
            address="123 Test St",
            address2="Apt 1",
            state="CA",
            city="Test City",
            timezone="America/Los_Angeles"
        )
        self.assertEqual(brand_owner.name, "Test Brand")
        self.assertEqual(brand_owner.description, "This is a test brand owner.")
        self.assertEqual(brand_owner.public_business_name, "Test Public Name")
        self.assertEqual(brand_owner.email, "test@example.com")
        self.assertEqual(brand_owner.phone_number, "1234567890")
        self.assertEqual(brand_owner.account_name, "testaccount")
        self.assertEqual(brand_owner.zip_code, "12345")
        self.assertEqual(brand_owner.address, "123 Test St")
        self.assertEqual(brand_owner.address2, "Apt 1")
        self.assertEqual(brand_owner.state, "CA")
        self.assertEqual(brand_owner.city, "Test City")
        self.assertEqual(brand_owner.timezone, "America/Los_Angeles")

    def test_read_brandowner_instance(self):
        brand_owner = BrandOwner.objects.create(
            name="Test Brand",
            description="This is a test brand owner.",
            public_business_name="Test Public Name",
            email="test@example.com",
            phone_number="1234567890",
            account_name="testaccount",
            zip_code="12345",
            address="123 Test St",
            address2="Apt 1",
            state="CA",
            city="Test City",
            timezone="America/Los_Angeles"
        )

        read_brand_owner = BrandOwner.objects.get(id=brand_owner.id)
        self.assertEqual(read_brand_owner.name, "Test Brand")
        self.assertEqual(read_brand_owner.description, "This is a test brand owner.")
        self.assertEqual(read_brand_owner.public_business_name, "Test Public Name")
        self.assertEqual(read_brand_owner.email, "test@example.com")
        self.assertEqual(read_brand_owner.phone_number, "1234567890")
        self.assertEqual(read_brand_owner.account_name, "testaccount")
        self.assertEqual(read_brand_owner.zip_code, "12345")
        self.assertEqual(read_brand_owner.address, "123 Test St")
        self.assertEqual(read_brand_owner.address2, "Apt 1")
        self.assertEqual(read_brand_owner.state, "CA")
        self.assertEqual(read_brand_owner.city, "Test City")
        self.assertEqual(read_brand_owner.timezone, "America/Los_Angeles")

    def test_update_brandowner_instance(self):
        brand_owner = BrandOwner.objects.create(
            name="Test Brand",
            description="This is a test brand owner.",
            public_business_name="Test Public Name",
            email="test@example.com",
            phone_number="1234567890",
            account_name="testaccount",
            zip_code="12345",
            address="123 Test St",
            address2="Apt 1",
            state="CA",
            city="Test City",
            timezone="America/Los_Angeles"
        )

        brand_owner.name = "Updated Brand"
        brand_owner.description = "Updated description."
        brand_owner.public_business_name = "Updated Public Name"
        brand_owner.email = "updated@example.com"
        brand_owner.phone_number = "0987654321"
        brand_owner.account_name = "updatedaccount"
        brand_owner.zip_code = "54321"
        brand_owner.address = "321 Updated St"
        brand_owner.address2 = "Apt 2"
        brand_owner.state = "NY"
        brand_owner.city = "Updated City"
        brand_owner.timezone = "America/New_York"
        brand_owner.save()

        updated_brand_owner = BrandOwner.objects.get(id=brand_owner.id)
        self.assertEqual(updated_brand_owner.name, "Updated Brand")
        self.assertEqual(updated_brand_owner.description, "Updated description.")
        self.assertEqual(updated_brand_owner.public_business_name, "Updated Public Name")
        self.assertEqual(updated_brand_owner.email, "updated@example.com")
        self.assertEqual(updated_brand_owner.phone_number, "0987654321")
        self.assertEqual(updated_brand_owner.account_name, "updatedaccount")
        self.assertEqual(updated_brand_owner.zip_code, "54321")
        self.assertEqual(updated_brand_owner.address, "321 Updated St")
        self.assertEqual(updated_brand_owner.address2, "Apt 2")
        self.assertEqual(updated_brand_owner.state, "NY")
        self.assertEqual(updated_brand_owner.city, "Updated City")
        self.assertEqual(updated_brand_owner.timezone, "America/New_York")

    def test_delete_brandowner_instance(self):
        brand_owner = BrandOwner.objects.create(
            name="Test Brand",
            description="This is a test brand owner.",
            public_business_name="Test Public Name",
            email="test@example.com",
            phone_number="1234567890",
            account_name="testaccount",
            zip_code="12345",
            address="123 Test St",
            address2="Apt 1",
            state="CA",
            city="Test City",
            timezone="America/Los_Angeles"
        )

        brand_owner_id = brand_owner.id
        brand_owner.delete()

        with self.assertRaises(BrandOwner.DoesNotExist):
            BrandOwner.objects.get(id=brand_owner_id)