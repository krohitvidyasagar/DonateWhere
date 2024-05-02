from django.test import TestCase, RequestFactory

from donation.models import UserType, User
from donation.views import LoginView, UserRegistrationView


class UserLoginRegistrationTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

        self.user = User.objects.create(first_name='Rohit', last_name='V', email='rohit.v@tmail.com',
                                        phone='2221113333', password='123456', user_type=UserType.PERSONAL.value,
                                        address='123 Tanger Lane, San Antonio, TX')

    # def test_login(self):
    #     payload = {
    #         'email': self.user.email,
    #         'password': self.user.password
    #     }
    #
    #     request = self.factory.post('api/login', data=payload, content_type='application/json')
    #
    #     response = LoginView.as_view()(request)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data['user']['id'], str(self.user.id))

    def test_register(self):
        payload = {
            'email': 'dhanush.s@tmail.com',
            'password': '6789012345',
            'first_name': 'Dhanush',
            'last_name': 'S',
            'user_type': UserType.PERSONAL.value,
            'phone': '5551112222'
        }

        request = self.factory.post('api/register', data=payload, content_type='application/json')
        response = UserRegistrationView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('detail', response.data)

        payload_2 = {
            'email': 'dhanush.s@tmail.com',
            'password': '6789012345'
        }

        request = self.factory.post('api/login', data=payload_2, content_type='application/json')

        response = LoginView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user']['email'], payload_2['email'])
