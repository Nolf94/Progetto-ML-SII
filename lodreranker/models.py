# lodreranker/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=180, blank=True)
    last_name = models.CharField(max_length=180, blank=True)
    age = models.SmallIntegerField(blank=True, null=True)
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
#   user = models.OneToOneField(User, on_delete=models.CASCADE)

    social_uid = models.CharField(max_length=100, blank=True, null=True)

    has_social = models.BooleanField(default=False)
    has_demographic = models.BooleanField(default=False)
    has_vector = models.BooleanField(default=False)