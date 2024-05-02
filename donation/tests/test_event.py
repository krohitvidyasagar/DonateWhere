from datetime import datetime

from django.test import TestCase, RequestFactory

from donation.models import UserType, User, Event
from donation.views import EventListCreateView, EventUpdateDeleteView


def user_authentication(request, user):
    request._force_auth_user = user
    data = {
        'user': user.email
    }
    request.auth_context = data


class EventTest(TestCase):
    BASE_URL = 'api/event'

    def setUp(self):
        self.factory = RequestFactory()

    @classmethod
    def setUpTestData(cls):
        cls.org = User.objects.create(first_name='Hope Haven', email='hope.haven@tmail.com',
                                       phone='5551112222', password='345678', user_type=UserType.ORGANIZATION.value,
                                       address='689 Wilma Lane, Dallas, TX')

        cls.event = Event.objects.create(organization=cls.org, name='Clothing Drive',
                                         description='We are going to be giving away clothes', address='Dallas, TX',
                                         datetime=datetime.now())

    def test_list_events(self):
        request = self.factory.get(self.BASE_URL)

        user_authentication(request, self.org)

        response = EventListCreateView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_create_event(self):
        payload = {
            'name': 'Farmers Market Donation Drive',
            'description': 'Groceries galore',
            'datetime': '2024-04-26T12:00:00'
        }
        request = self.factory.post(self.BASE_URL, data=payload, content_type='application/json')

        user_authentication(request, self.org)

        response = EventListCreateView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], payload['name'])

    def test_update_event(self):
        payload = {
            'description': 'new description'
        }

        url = f'{self.BASE_URL}/{self.event.id}'
        request = self.factory.patch(url, data=payload, content_type='application/json')

        user_authentication(request, self.org)

        response = EventUpdateDeleteView.as_view()(request, pk=str(self.event.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['description'], payload['description'])

    def test_delete_event(self):
        url = f'{self.BASE_URL}/{self.event.id}'
        request = self.factory.delete(url)

        user_authentication(request, self.org)

        response = EventUpdateDeleteView.as_view()(request, pk=str(self.event.id))
        self.assertEqual(response.status_code, 204)

