# lodreranker/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
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


class CustomUserDemographicDataForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('age','gender',)

    # tentative prepopulation with data from User Social Account
    # def __init__(self, *args, **kwargs):
    #     super(UserCreationForm, self).__init__(*args, **kwargs)
    
    #     if hasattr(self, 'sociallogin'):
    #         print(True)
            
    #         # if 'gender' in self.sociallogin.account.extra_data:
    #         #     if self.sociallogin.account.extra_data['gender'] == 'male':
    #         #         self.initial['gender'] = 'M'
    #         #     elif self.sociallogin.account.extra_data['gender'] == 'female':
    #         #         self.initial['gender'] = 'F'


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields

        def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                del self.fields['password']


class CreatePasswordForm(forms.Form):
    password = forms.CharField(label='Password',  widget=forms.PasswordInput())





# class DemographicForm(forms.Form):
#     df_username = forms.CharField(label='Username', max_length=180)
#     df_password = forms.CharField(label='Password',  widget=forms.PasswordInput())

#     df_firstname = forms.CharField(label='First name', max_length=180)
#     df_lastname = forms.CharField(label='Last name', max_length=180)

