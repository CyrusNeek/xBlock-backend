from web.models.reservation import Reservation
from web.tests.base_test import BaseTest
from django.utils import timezone

class ReservationTestCase(BaseTest):       
    def setUp(self):
        super().setUp()
        self.reservation_data = {
            'first_name': 'John',
            'unit': self.unit,
            'last_name': 'Doe',
            'email': 'john.doe2@example.com',
            'phone_number': '1234567810',
            'party_size': 4,
            'reservation_date': timezone.now().date(),
            'reservation_time': timezone.now().time(),
            'area': 'Main Hall',
            'tables': 'Table 1, Table 2',
            'server_name': 'Alice',
            'tags': 'VIP',
            'notes': 'Special requests',
            'experience': 'Great experience'
        }
        self.reservation = Reservation.objects.create(**self.reservation_data)
        
    def test_create_reservation(self):
        self.assertIsNotNone(self.reservation)
        
    def test_read_reservation(self):
        self.assertEqual(self.reservation.first_name, 'John')
        
    def test_update_reservation(self):
        self.reservation.first_name = 'Jane'
        self.reservation.save()
        self.assertEqual(self.reservation.first_name, 'Jane')

    def test_delete_reservation(self):
        reservation_id = self.reservation.id
        self.reservation.delete()
        with self.assertRaises(Reservation.DoesNotExist):
            Reservation.objects.get(id=reservation_id)