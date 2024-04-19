from rest_framework import serializers

from donation.models import User


class UserLoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'phone']
