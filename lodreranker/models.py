# lodreranker/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=180, blank=True, null=True)
    last_name = models.CharField(max_length=180, blank=True, null=True)
    age = models.SmallIntegerField(blank=True, null=True)
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    has_social = models.BooleanField(default=False)
    has_demographic = models.BooleanField(default=False)
    has_poivector = models.BooleanField(default=False)
    has_movvector = models.BooleanField(default=False)
    poi_weights = models.TextField(blank=True, null=True)
    mov_weights = models.TextField(blank=True, null=True)
    

    # UNUSED
    # social_uid = models.CharField(max_length=100, blank=True, null=True)
    # user = models.OneToOneField(User, on_delete=models.CASCADE)