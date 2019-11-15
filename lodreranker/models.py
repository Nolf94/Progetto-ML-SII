# lodreranker/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from social_django.fields import JSONField
from lodreranker import constants

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
    poi_weights = JSONField(blank=True, null=True)

    has_movies = models.BooleanField(default=False)
    social_movies = JSONField(blank=True, null=True)
    form_movies = JSONField(blank=True, null=True)
    
class RetrievedItem(models.Model):
    wkd_id = models.CharField(max_length=30, primary_key=True)
    MEDIA_CHOICES = [
        (constants.MOVIE, 'Movie'),
        (constants.BOOK, 'Book'),
        (constants.MUSIC, 'Music')
    ]
    media_type = models.IntegerField(choices=MEDIA_CHOICES)
    name = models.CharField(max_length=180, blank=True, null=True)
    querystring = models.CharField(max_length=180, blank=True, null=True)
    abstract = models.TextField(blank=True, null=True)
    vector = JSONField(blank=True, null=True)