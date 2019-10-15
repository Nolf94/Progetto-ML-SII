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
        fields = ('username','first_name','last_name','age','gender',)

    # tentative prepopulation with data from User Social Account
    # def __init__(self, *args, **kwargs):
    #     super(CustomUserDemographicDataForm, self).__init__(*args, **kwargs)
            # if 'gender' in self.sociallogin.account.extra_data:
            #     if self.sociallogin.account.extra_data['gender'] == 'male':
            #         self.initial['gender'] = 'M'
            #     elif self.sociallogin.account.extra_data['gender'] == 'female':
            #         self.initial['gender'] = 'F'


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            del self.fields['password']
