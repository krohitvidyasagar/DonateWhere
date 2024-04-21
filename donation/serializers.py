from rest_framework import serializers

from donation.models import User, Donation


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
        fields = ['id', 'first_name', 'last_name', 'email', 'address', 'profile_photo_base64']


class DonationSerializer(serializers.ModelSerializer):
    donated_by = serializers.SerializerMethodField()

    class Meta:
        model = Donation
        fields = ['id', 'item', 'category', 'datetime', 'is_claimed', 'created_at', 'donated_by']

    def get_donated_by(self, obj):
        owner = User.objects.get(id=obj.donated_by.id)
        return DonationOwnerSerializer(owner).data
