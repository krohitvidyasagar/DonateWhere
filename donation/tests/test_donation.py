from datetime import datetime

from django.test import TestCase, RequestFactory

from donation.models import UserType, User, Donation, Claim
from donation.views import DonationListCreateView, DonationRetrievePutDeleteView, ClaimListView, DonationClaimView


def user_authentication(request, user):
    request._force_auth_user = user
    data = {
        'user': user.email
    }
    request.auth_context = data


class DonationTest(TestCase):
    BASE_URL = 'api/donation'

    def setUp(self):
        self.factory = RequestFactory()

        self.user = User.objects.create(first_name='Rohit', last_name='V', email='rohit.v@tmail.com',
                                        phone='2221113333', password='123456', user_type=UserType.PERSONAL.value,
                                        address='123 Tanger Lane, San Antonio, TX')


    @classmethod
    def setUpTestData(cls):
        cls.user_2 = User.objects.create(first_name='Dhanush', last_name='S', email='dhanush.s@tmail.com',
                                         phone='4441115555', password='789012', user_type=UserType.PERSONAL.value,
                                         address='415 Hopkins Lane, Dallas, TX')

        cls.donation_1 = Donation.objects.create(donated_by=cls.user_2, item='T-Shirts', category='Clothing',
                                                 description='5 Red Tshirts', datetime=datetime.now(),
                                                 address='415 Hopkins Lane, Dallas, TX')

        cls.donation_2 = Donation.objects.create(donated_by=cls.user_2, item='Shorts', category='Clothing',
                                                 description='3 Black Shorts', datetime=datetime.now(),
                                                 address='415 Hopkins Lane, Dallas, TX')

        cls.organization = User.objects.create(first_name='Hope Haven', email='hope.haven@tmail.com',
                                               phone='5551112222', password='345678',
                                               user_type=UserType.ORGANIZATION.value,
                                               address='689 Wilma Lane, Dallas, TX')

        cls.claim = Claim.objects.create(donation=cls.donation_1, claimant=cls.organization, claimed_on=datetime.now())

    def test_create_donation(self):
        payload = {
            'item': 'Manual coffee grinder',
            'category': 'Kitchen tools',
            'datetime': '2024-04-22T12:30:00Z'
        }

        request = self.factory.post(self.BASE_URL, data=payload, content_type='application/json')

        user_authentication(request, self.user)

        response = DonationListCreateView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['item'], payload['item'])

    def test_list_donation_user(self):
        request = self.factory.get(self.BASE_URL)

        user_authentication(request, self.user)

        response = DonationListCreateView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)

    def test_list_donation_organization(self):
        request = self.factory.get(self.BASE_URL)

        user_authentication(request, self.organization)

        response = DonationListCreateView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)

    def test_update_donation(self):
        payload = {
            'description': '4 black shorts'
        }

        url = f'{self.BASE_URL}/{self.donation_2.id}'
        request = self.factory.patch(url, data=payload, content_type='application/json')

        user_authentication(request, self.user)

        response = DonationRetrievePutDeleteView.as_view()(request, pk=str(self.donation_2.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['description'], payload['description'])

    def test_delete_donation(self):
        url = f'{self.BASE_URL}/{self.donation_2.id}'
        request = self.factory.delete(url)

        user_authentication(request, self.user)

        response = DonationRetrievePutDeleteView.as_view()(request, pk=str(self.donation_2.id))
        self.assertEqual(response.status_code, 204)

    def test_retrieve_donation(self):
        url = f'{self.BASE_URL}/{self.donation_2.id}'
        request = self.factory.get(url)

        user_authentication(request, self.user)

        response = DonationRetrievePutDeleteView.as_view()(request, pk=str(self.donation_2.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], str(self.donation_2.id))

    def test_list_claim(self):
        url = 'api/claim'
        request = self.factory.get(url)

        user_authentication(request, self.organization)

        response = ClaimListView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_create_claim(self):
        url = f'api/donation/{self.donation_2.id}/claim'
        request = self.factory.post(url)

        user_authentication(request, self.organization)

        response = DonationClaimView.as_view()(request, pk=str(self.donation_2.id))
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.data['donation']['id'], str(self.donation_2.id))
        self.assertEquals(response.data['claimant']['id'], str(self.organization.id))

    def delete_claim(self):
        url = f'api/donation/{self.donation_1.id}/claim'
        request = self.factory.delete(url)

        response = DonationClaimView.as_view()(request, pk=str(self.donation_1.id))
        self.assertEqual(response.status_code, 200)
        self.assertIn('detail', response.data)
