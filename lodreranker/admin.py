# lodreranker/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, Group

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, RetrievedItem, RankerMetric, BeyondAccuracyMetric

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ['username', 'gender', 'age', 'profession', 'social_movies_count', 'social_books_count', 'social_artists_count', 'has_social_connect', 'has_social_data', 'has_demographic', 'has_movies', 'has_books', 'has_artists']
    fieldsets = ((('User'), {'fields': ('gender', 'age', 'profession', 'form_movies', 'form_books', 'form_artists', 'social_items')}),) + UserAdmin.fieldsets

class RetrievedItemAdmin(admin.ModelAdmin):
    list_display = ['wkd_id', 'updated', 'media_type', 'name', 'querystring', 'outdegree']


class RankerMetricAdmin(admin.ModelAdmin):
    list_display = ['created','retriever', 'clustering', 'summarize', 'outdegree']


class BeyondAccuracyMetricAdmin(admin.ModelAdmin):
    list_display = ['created','retriever', 'rating', 'novelty', 'serendipity', 'diversity']


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(RetrievedItem, RetrievedItemAdmin)
admin.site.unregister(Group)
admin.site.register(RankerMetric, RankerMetricAdmin)
admin.site.register(BeyondAccuracyMetric, BeyondAccuracyMetricAdmin)
