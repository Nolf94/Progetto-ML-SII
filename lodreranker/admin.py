# lodreranker/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, Group

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, RetrievedItem

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ['username', 'has_social_connect', 'has_social_data', 'has_demographic', 'has_movies', 'has_books', 'has_artists' ]
    fieldsets = ((('User'), {'fields': ('age', 'gender', 'form_movies', 'form_books','form_artists', 'social_items')}),) + UserAdmin.fieldsets

class RetrievedItemAdmin(admin.ModelAdmin):
    list_display = ['wkd_id', 'updated', 'media_type', 'name', 'querystring']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(RetrievedItem, RetrievedItemAdmin)
admin.site.unregister(Group)

