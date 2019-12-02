# lodreranker/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from social_django.fields import JSONField
from lodreranker import constants

class RetrievedItem(models.Model):
    wkd_id = models.CharField(max_length=30, primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    MEDIA_CHOICES = [
        (constants.MOVIE, constants.MOVIE),
        (constants.BOOK, constants.BOOK),
        (constants.MUSIC, constants.MUSIC)
    ]
    media_type = models.CharField(max_length=30, choices=MEDIA_CHOICES)
    name = models.CharField(max_length=180, blank=True, null=True)
    querystring = models.CharField(max_length=180, blank=True, null=True)
    abstract = models.TextField(blank=True, null=True)
    vector = JSONField(blank=True, null=True)
    outdegree = models.PositiveSmallIntegerField(default=0)


class RankerMetric(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    retriever = models.CharField(max_length=20)
    clustering = models.PositiveIntegerField(null=True)
    summarize = models.PositiveIntegerField(null=True)
    outdegree = models.PositiveIntegerField(null=True)

class BeyondAccuracyMetric(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    retriever = models.CharField(max_length=20)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    novelty = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    serendipity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    diversity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])


class CustomUser(AbstractUser):
    # first_name = models.CharField(max_length=180, blank=True, null=True)
    # last_name = models.CharField(max_length=180, blank=True, null=True)
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True)
    age = models.SmallIntegerField(null=True)
    PROFESSION_CHOICES = [('S', 'Student'),('T', 'Teacher'),('E', 'Employee'),('F', 'Freelancer'),('U','Unemployed')]
    profession = models.CharField(max_length=10, choices=PROFESSION_CHOICES, null=True)
    has_social_connect = models.BooleanField(default=False)
    has_social_data = models.BooleanField(default=False)
    has_demographic = models.BooleanField(default=False)
    
    # has_poivector = models.BooleanField(default=False)
    # poi_weights = JSONField(blank=True, null=True)
    has_movies = models.BooleanField(default=False)
    form_movies = JSONField(blank=True, null=True)
    has_books = models.BooleanField(default=False)
    form_books = JSONField(blank=True, null=True)
    has_artists = models.BooleanField(default=False)
    form_artists = JSONField(blank=True, null=True)

    completed = models.BooleanField(default=False)
    social_items = models.ManyToManyField(RetrievedItem)
