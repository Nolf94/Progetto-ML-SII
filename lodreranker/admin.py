# lodreranker/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin, Group

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ['username', 'email']
    fieldsets = ((('User'), {'fields': ('age', 'gender')}),) + UserAdmin.fieldsets

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.unregister(Group)
