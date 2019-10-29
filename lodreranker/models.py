# lodreranker/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from social_django.fields import JSONField

class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=180, blank=True, null=True)
    last_name = models.CharField(max_length=180, blank=True, null=True)
    age = models.SmallIntegerField(blank=True, null=True)
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    has_social_connect = models.BooleanField(default=False)
    has_social_data = models.BooleanField(default=False)
    has_demographic = models.BooleanField(default=False)
    has_poivector = models.BooleanField(default=False)
    has_movies = models.BooleanField(default=False)
    poi_weights = JSONField(blank=True, null=True)
    social_movies = JSONField(blank=True, null=False)
    form_movies = JSONField(blank=True, null=True)
    
    # UNUSED
    # social_uid = models.CharField(max_length=100, blank=True, null=True)
    # user = models.OneToOneField(User, on_delete=models.CASCADE)