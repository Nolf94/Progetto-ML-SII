# lodreranker/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username','password1','password2','age','gender',)

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        
        # remove helper texts
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None

        if hasattr(self, 'sociallogin'):
            print(True)
            
            # if 'gender' in self.sociallogin.account.extra_data:
            #     if self.sociallogin.account.extra_data['gender'] == 'male':
            #         self.initial['gender'] = 'M'
            #     elif self.sociallogin.account.extra_data['gender'] == 'female':
            #         self.initial['gender'] = 'F'


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields


class CreatePasswordForm(forms.Form):
    password = forms.CharField(label='Password',  widget=forms.PasswordInput())





class DemographicForm(forms.Form):
    df_username = forms.CharField(label='Username', max_length=180)
    df_password = forms.CharField(label='Password',  widget=forms.PasswordInput())

    df_firstname = forms.CharField(label='First name', max_length=180)
    df_lastname = forms.CharField(label='Last name', max_length=180)

