from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework.exceptions import AuthenticationFailed, ParseError
from rest_framework.response import Response

from donation.models import User
from donation.serializers import UserLoginSerializer, UserProfileSerializer
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

            return Response({'detail': 'User has been successfully registered'})


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
