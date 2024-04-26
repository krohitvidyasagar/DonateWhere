import base64

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Q
from rest_framework import generics
from rest_framework.exceptions import AuthenticationFailed, ParseError
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from donation.filters import DonationFilter
from donation.models import User, Donation, UserType, Claim, Message, Conversation
from donation.serializers import UserLoginSerializer, UserProfileSerializer, DonationListSerializer, ClaimSerializer, \
    ConversationSerializer, ConversationListSerializer, DonationSerializer
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


class ProfileView(generics.ListAPIView, generics.UpdateAPIView):
    name = 'user-profile-view'
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer

    def get(self, request, *args, **kwargs):
        email = self.request.auth_context['user']
        user = User.objects.get(email=email)

        return Response(self.get_serializer(user).data)

    def patch(self, request, *args, **kwargs):
        email = self.request.auth_context['user']
        user = User.objects.get(email=email)

        serializer = UserProfileSerializer(user, data=self.request.data, partial=True)
        serializer.is_valid()
        serializer.save()

        return Response(serializer.data)


class DonationListCreateView(generics.ListCreateAPIView):
    name = 'donation-list-create-view'
    queryset = Donation.objects.all()
    serializer_class = DonationListSerializer
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
        image_base64 = self.request.data.get('image_base64')
        address = self.request.data.get('address')
        description = self.request.data.get('description')

        donation = Donation.objects.create(donated_by=user, item=item, category=category, datetime=datetime,
                                           address=address, image_base64=image_base64, description=description)

        serializer = self.get_serializer(donation)

        return Response(serializer.data)


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


class ConversationListCreateView(generics.ListCreateAPIView):
    name = 'conversation-list-create-view'
    queryset = Conversation.objects.all()
    serializer_class = ConversationListSerializer

    def get_queryset(self):
        email = self.request.auth_context['user']
        user = User.objects.get(email=email)

        return super().get_queryset().filter(Q(initiator=user) | Q(receiver=user))

    def post(self, request, *args, **kwargs):
        email = self.request.auth_context['user']
        sender = User.objects.get(email=email)

        receiver_email = self.request.data.get('receiver')
        receiver = User.objects.get(email=receiver_email)

        text = self.request.data.get('text')

        if request.data.get('conversation_id'):
            conversation_id = request.data.get('conversation_id')
            conversation = Conversation.objects.get(id=conversation_id)

        else:
            conversation = Conversation.objects.create(initiator=sender, receiver=receiver)

        message = Message.objects.create(conversation=conversation, sender=sender, text=text)
        serializer = ConversationSerializer(conversation)

        return Response(serializer.data)


class MessageListView(generics.ListAPIView):
    name = 'message-list-view'
    queryset = Message.objects.all()

    def get(self, request, *args, **kwargs):
        conversation_id = self.kwargs['conversation_id']
        conversation = Conversation.objects.get(id=conversation_id)

        serializer = ConversationSerializer(conversation)

        return Response(serializer.data)


class ImageUploadView(generics.CreateAPIView):
    name = 'image-upload-view'
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        email = self.request.auth_context['user']
        user = User.objects.get(email=email)

        if self.request.FILES and 'profile' in self.request.FILES:
            profile_photo = self.request.FILES['profile_photo']
            profile_photo_base64 = base64.b64encode(profile_photo.read()).decode('utf-8')
            user.profile_photo_base64 = profile_photo_base64

            user.save()

            return Response({'detail': 'User profile image uploaded successfully.'})

        elif self.request.FILES and 'donation' in self.request.FILES:
            donation_photo = self.request.FILES['donation']
            donation_id = self.request.data['donation_id']

            donation = Donation.objects.get(id=donation_id)

            donation_photo_base64 = base64.b64encode(donation_photo.read()).decode('utf-8')
            donation.image_base64 = donation_photo_base64

            donation.save()

            return Response({'detail': 'Donation image uploaded successfully.'})
