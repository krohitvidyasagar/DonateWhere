import uuid
from enum import Enum

from django.db import models


class UserType(Enum):
    PERSONAL = 'PERSONAL'
    ORGANIZATION = 'ORGANIZATION'


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    first_name = models.CharField(max_length=30, null=True)
    last_name = models.CharField(max_length=40, null=True)

    email = models.EmailField(max_length=100, null=False, unique=True)
    phone = models.CharField(max_length=20, null=True)
    password = models.CharField(max_length=100, null=False)
    user_type = models.CharField(max_length=20, null=False, default=UserType.PERSONAL.value)
    address = models.TextField(null=True)

    profile_photo_base64 = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user'
        ordering = ['-created_at']


class Donation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    donated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.CharField(max_length=100, null=False)
    category = models.CharField(max_length=50, null=False)
    description = models.TextField(null=True)
    datetime = models.DateTimeField(null=False)
    is_claimed = models.BooleanField(default=False)
    image_base64 = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'donation'
        ordering = ['-created_at']


class Claim(models.Model):
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE, null=False)
    claimant = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    claimed_on = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'claim'
        ordering = ['-claimed_on']
        unique_together = ['donation', 'claimant']

