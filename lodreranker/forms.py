# lodreranker/forms.py
from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username','password1','password2')

    # remove helper texts
    # def __init__(self, *args, **kwargs):
    #     super(UserCreationForm, self).__init__(*args, **kwargs)
    #     for fieldname in ['username', 'password1', 'password2']:
    #         self.fields[fieldname].help_text = None


class CustomUserDemographicDataForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('gender', 'age', 'profession',)
        # fields = ('username','gender', 'age', 'profession',)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            del self.fields['password']
