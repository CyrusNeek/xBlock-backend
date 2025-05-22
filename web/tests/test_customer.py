from web.models.customer import Customer
from web.tests.base_test import BaseTest

class CustomerTestCase(BaseTest):
    def setUp(self):
        super().setUp()
        self.customer = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="1234567890"
        )
        
    
    
    def test_create_customer_with_required_fields(self):
        
        self.assertEqual(self.customer.first_name, "John")
        self.assertEqual(self.customer.last_name, "Doe")
        self.assertEqual(self.customer.email, "john.doe@example.com")
        self.assertEqual(self.customer.phone_number, "1234567890")

    def test_read_customer_instance(self):
        read_customer = Customer.objects.get(id=self.customer.id)
        self.assertEqual(read_customer.first_name, "John")
        self.assertEqual(read_customer.last_name, "Doe")
        self.assertEqual(read_customer.email, "john.doe@example.com")
        self.assertEqual(read_customer.phone_number, "1234567890")

    def test_update_customer_instance(self):
        self.customer.first_name = "Jane"
        self.customer.last_name = "Smith"
        self.customer.email = "jane.smith@example.com"
        self.customer.phone_number = "0987654321"
        self.customer.save()

        updated_customer = Customer.objects.get(id=self.customer.id)
        self.assertEqual(updated_customer.first_name, "Jane")
        self.assertEqual(updated_customer.last_name, "Smith")
        self.assertEqual(updated_customer.email, "jane.smith@example.com")
        self.assertEqual(updated_customer.phone_number, "0987654321")

    def test_delete_customer_instance(self):
        customer_id = self.customer.id
        self.customer.delete()

        with self.assertRaises(Customer.DoesNotExist):
            Customer.objects.get(id=customer_id)