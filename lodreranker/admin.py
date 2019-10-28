# lodreranker/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, Group

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ['username', 'has_social_connect', 'has_social_data', 'has_demographic', 'has_poivector', 'has_moviesmodel' ]
    fieldsets = ((('User'), {'fields': ('age', 'gender', 'poi_weights', 'moviesmodel')}),) + UserAdmin.fieldsets

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.unregister(Group)
