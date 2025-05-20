from web.models.brand import Brand
from web.models.brand_owner import BrandOwner
from web.tests.base_test import BaseTest

class BrandTestCase(BaseTest):
    def test_create_brand_with_all_fields(self):
        owner = BrandOwner.objects.create(
            name="Test Owner",
            description="Test Description",
            public_business_name="Test Business",
            email="test@example.com",
            phone_number="1234567890",
            account_name="test_account",
            zip_code="12345",
            address="123 Test St",
            address2="Apt 1",
            state="CA",
            city="Test City",
            timezone="America/Chicago"
        )

        brand = Brand.objects.create(
            name="Test Brand",
            owner=owner,
            description="Test Brand Description",
            website="http://www.testbrand.com"
        )

        self.assertEqual(brand.name, "Test Brand")
        self.assertEqual(brand.owner, owner)
        self.assertEqual(brand.description, "Test Brand Description")
        self.assertEqual(brand.website, "http://www.testbrand.com")

    def test_read_brand_instance(self):
        owner = BrandOwner.objects.create(
            name="Test Owner",
            description="Test Description",
            public_business_name="Test Business",
            email="test@example.com",
            phone_number="1234567890",
            account_name="test_account",
            zip_code="12345",
            address="123 Test St",
            address2="Apt 1",
            state="CA",
            city="Test City",
            timezone="America/Chicago"
        )

        brand = Brand.objects.create(
            name="Test Brand",
            owner=owner,
            description="Test Brand Description",
            website="http://www.testbrand.com"
        )

        read_brand = Brand.objects.get(id=brand.id)
        self.assertEqual(read_brand.name, "Test Brand")
        self.assertEqual(read_brand.owner, owner)
        self.assertEqual(read_brand.description, "Test Brand Description")
        self.assertEqual(read_brand.website, "http://www.testbrand.com")

    def test_update_brand_instance(self):
        owner = BrandOwner.objects.create(
            name="Test Owner",
            description="Test Description",
            public_business_name="Test Business",
            email="test@example.com",
            phone_number="1234567890",
            account_name="test_account",
            zip_code="12345",
            address="123 Test St",
            address2="Apt 1",
            state="CA",
            city="Test City",
            timezone="America/Chicago"
        )

        brand = Brand.objects.create(
            name="Test Brand",
            owner=owner,
            description="Test Brand Description",
            website="http://www.testbrand.com"
        )

        brand.name = "Updated Brand"
        brand.description = "Updated Brand Description"
        brand.website = "http://www.updatedbrand.com"
        brand.save()

        updated_brand = Brand.objects.get(id=brand.id)
        self.assertEqual(updated_brand.name, "Updated Brand")
        self.assertEqual(updated_brand.owner, owner)
        self.assertEqual(updated_brand.description, "Updated Brand Description")
        self.assertEqual(updated_brand.website, "http://www.updatedbrand.com")

    def test_delete_brand_instance(self):
        owner = BrandOwner.objects.create(
            name="Test Owner",
            description="Test Description",
            public_business_name="Test Business",
            email="test@example.com",
            phone_number="1234567890",
            account_name="test_account",
            zip_code="12345",
            address="123 Test St",
            address2="Apt 1",
            state="CA",
            city="Test City",
            timezone="America/Chicago"
        )

        brand = Brand.objects.create(
            name="Test Brand",
            owner=owner,
            description="Test Brand Description",
            website="http://www.testbrand.com"
        )

        brand_id = brand.id
        brand.delete()