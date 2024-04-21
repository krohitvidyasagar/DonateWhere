from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from rest_framework import generics
from rest_framework.exceptions import AuthenticationFailed, ParseError
from rest_framework.response import Response

from donation.filters import DonationFilter
from donation.models import User, Donation, UserType, Claim
from donation.serializers import UserLoginSerializer, UserProfileSerializer, DonationSerializer, ClaimSerializer
from donation.services import AuthenticationUtils


class UserRegistrationView(generics.CreateAPIView):
    name = 'user-registration-view'
    queryset = User.objects.all()
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        email = self.request.data.get('email')

        # Check if the user already exists in the database
        try:
            user = User.objects.get(email=email)

            raise ParseError(detail='User with these email address already exists')

        except ObjectDoesNotExist:
            first_name = self.request.data.get('first_name')
            last_name = self.request.data.get('last_name')

            phone = self.request.data.get('phone')
            password = self.request.data.get('password')
            user_type = self.request.data.get('user_type')

            hashed_password = AuthenticationUtils.get_hashed_password(password.encode('utf-8'))

            user = User.objects.create(first_name=first_name, last_name=last_name,
                                       email=email.lower(), password=hashed_password)

            if phone:
                user.phone = phone
                user.save()

            if user_type:
                user.user_type = user_type
                user.save()

            return Response({'detail': 'User has been successfully registered.'})


class LoginView(generics.CreateAPIView):
    name = 'user-login-view'
    queryset = User.objects.all()
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        email = self.request.data['email']
        password = self.request.data['password']

        try:
            authenticated_user = User.objects.get(email__iexact=email)

            hashed_password = AuthenticationUtils.get_hashed_password(password.encode('utf-8'))

            if str(hashed_password) != authenticated_user.password:
                raise ObjectDoesNotExist()

            user_claims = AuthenticationUtils.get_user_claims(authenticated_user)

            access = AuthenticationUtils.get_user_access_token(user_claims)
            refresh = AuthenticationUtils.get_user_refresh_token(user_claims)

            return Response({
                'user': UserLoginSerializer(authenticated_user).data,
                'access': access,
                'refresh': refresh

            })

        except ObjectDoesNotExist:
            raise AuthenticationFailed(detail='Authentication Error')


class ProfileView(generics.ListAPIView):
    name = 'user-profile-view'
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer

    def get(self, request, *args, **kwargs):
        email = self.request.auth_context['user']
        user = User.objects.get(email=email)

        return Response(self.get_serializer(user).data)


class DonationListCreateView(generics.ListCreateAPIView):
    name = 'donation-list-create-view'
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    filterset_class = DonationFilter

    def get_queryset(self):
        email = self.request.auth_context['user']
        user = User.objects.get(email=email)
        if user.user_type == UserType.PERSONAL.value:
            return super().get_queryset().filter(donated_by_id=user.id)
        return super().get_queryset()

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        email = self.request.auth_context['user']
        user = User.objects.get(email=email)

        item = self.request.data.get('item')
        category = self.request.data.get('category')
        datetime = self.request.data.get('datetime')

        Donation.objects.create(donated_by=user, item=item, category=category, datetime=datetime)

        return Response({'detail': 'Donation has been created successfully.'})


class DonationRetrievePutDeleteView(generics.RetrieveUpdateDestroyAPIView):
    name = 'donation-retrieve-put-delete-view'
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'pk'

    def get_object(self):
        return super().get_object()

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class ClaimListView(generics.ListAPIView):
    name = 'donation-claim-view'
    queryset = Claim.objects.all()
    serializer_class = ClaimSerializer

    def get_queryset(self):
        email = self.request.auth_context['user']
        user = User.objects.get(email=email)

        if user.user_type == UserType.PERSONAL.value:
            return super().get_queryset().filter(donation__donated_by_id=user.id)
        else:
            return super().get_queryset().filter(claimant_id=user.id)


class DonationClaimView(generics.CreateAPIView, generics.DestroyAPIView):
    name = 'donation-claim-view'
    queryset = Claim.objects.all()
    serializer_class = ClaimSerializer

    def post(self, request, *args, **kwargs):
        email = self.request.auth_context['user']
        organization = User.objects.get(email=email)

        donation = Donation.objects.get(id=self.kwargs['pk'])

        try:
            claim = Claim.objects.create(donation=donation, claimant=organization)
        except IntegrityError:
            raise ParseError(detail='Donation has been already claimed by this organization.')

        donation.is_claimed = True
        donation.save()

        serializer = self.get_serializer(claim)

        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        email = self.request.auth_context['user']
        organization = User.objects.get(email=email)

        donation = Donation.objects.get(id=self.kwargs['pk'])

        try:
            claim = Claim.objects.get(donation_id=donation.id, claimant_id=organization.id)
            claim.delete()

            donation.is_claimed = False
            donation.save()

            return Response({'detail': 'Claim has been deleted successfully.'})
        except ObjectDoesNotExist:
            raise ParseError(detail='Claim does not exist.')
