from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.common.models import TimeStampedModel


class Role(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True, help_text="Street address, Apartment, etc.")
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    avatar = models.FileField(upload_to="avatars/", blank=True, null=True)
    is_active_customer = models.BooleanField(default=True)

    def __str__(self):
        return self.get_username()
