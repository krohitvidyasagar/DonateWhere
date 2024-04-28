from rest_framework import serializers

from donation.models import User, Donation, Claim, Message, Conversation, Event


class UserLoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'user_type']


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'user_type',
                  'address', 'profile_photo_base64']


class DonationOwnerSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'profile_photo_base64']


class DonationOwnerBasicSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']


class DonationListSerializer(serializers.ModelSerializer):
    donated_by = serializers.SerializerMethodField()

    class Meta:
        model = Donation
        fields = ['id', 'item', 'category', 'datetime', 'is_claimed', 'created_at', 'donated_by', 'address',
                  'image_base64']

    def get_donated_by(self, obj):
        owner = User.objects.get(id=obj.donated_by.id)
        return DonationOwnerBasicSerializer(owner).data


class DonationSerializer(serializers.ModelSerializer):
    donated_by = serializers.SerializerMethodField()

    class Meta:
        model = Donation
        fields = ['id', 'item', 'category', 'datetime', 'is_claimed', 'created_at', 'donated_by', 'address',
                  'description', 'image_base64']

    def get_donated_by(self, obj):
        owner = User.objects.get(id=obj.donated_by.id)
        return DonationOwnerSerializer(owner).data


class ClaimSerializer(serializers.ModelSerializer):

    donation = serializers.SerializerMethodField()
    claimant = serializers.SerializerMethodField()

    class Meta:
        model = Claim
        fields = ['donation', 'claimant', 'claimed_on']

    def get_donation(self, obj):
        return DonationListSerializer(obj.donation).data

    def get_claimant(self, obj):
        return UserProfileSerializer(obj.claimant).data


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['sender', 'text', 'timestamp']


class ConversationListSerializer(serializers.ModelSerializer):
    initiator = UserLoginSerializer()
    receiver = UserLoginSerializer()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'initiator', 'receiver', 'last_message']

    def get_last_message(self, instance):
        message = instance.message_set.last()
        return MessageSerializer(instance=message).data


class ConversationSerializer(serializers.ModelSerializer):
    initiator = UserLoginSerializer()
    receiver = UserLoginSerializer()
    message_set = MessageSerializer(many=True)

    class Meta:
        model = Conversation
        fields = ['id', 'initiator', 'receiver', 'message_set']


class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = ['id', 'name', 'description', 'datetime', 'created_at', 'organization']
