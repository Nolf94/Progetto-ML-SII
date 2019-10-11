from django.contrib.auth import login
from django.contrib.auth.backends import ModelBackend
from django.shortcuts import redirect
from django.urls import reverse_lazy
from social_django.models import UserSocialAuth

from .models import CustomUser

# Custom backend used for authentication in the is_skip pipeline step. 
# since django's ModelBackend only works with raw password but retrieved password from model is hashed.
class HashedPasswordAuthBackend(ModelBackend):
    def authenticate(self, username=None, hashed_pwd=None):
        try:
            return CustomUser.objects.get(username=username, password=hashed_pwd)
        except CustomUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None

# If session contains skip_creation=True, then skip the social auth pipeline and try to login the user:
# - If the user social auth exists, authenticate, login and redirect to home
# - If the user social auth does not exists, redirect to login
def is_skip(strategy, backend, user, response, *args, **kwargs):
    if strategy.session_get('skip_creation') is True: # interrupt the pipeline
        soc_auths = UserSocialAuth.objects.filter(uid=kwargs['uid'])
        if soc_auths:
            user = soc_auths[0].user
            username = user.username
            hashed_pwd = user.password # password from model is hashed
            authenticated_user = HashedPasswordAuthBackend().authenticate(username, hashed_pwd)
            login(strategy.request, authenticated_user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect(reverse_lazy('home'))
        else:
            # TODO add a parameter to render the error in the login page
            return redirect(reverse_lazy('login')) 
    else:
        return # continue the pipeline


def redirect_registration(strategy, backend, user, response, *args, **kwargs):
    # UNUSED
    # user.social_uid = kwargs['uid']
    user.has_social = True
    user.save()
    return redirect(reverse_lazy('signup_s2'))



####################################################################################################

# @partial
# def s0(strategy, backend, request, details, *args, **kwargs):
#     local_password = strategy.session_get('local_password', None)
#     if not local_password:
#         return redirect(reverse('s0_createpassword'))

#     user = CustomUser.objects.get(id=kwargs['user'].id)
#     user.set_password(local_password)
#     user.save()

#     return


# @partial
# def s1(strategy, backend, request, details, *args, **kwargs):
#     ok = strategy.session_get('ok', None)

#     if not ok:
#         return redirect(reverse('s1_additionaldata'))
    
#     return




# @partial
# def custom_step(strategy, backend, request, details, *args, **kwargs):

#     strategy.session_set('uid', kwargs['uid'])

#     myobj = {'field1': 111}
#     strategy.session_set('myobj', myobj)

#     # request.session['myobj'] = myobj


#     # print((kwargs))

#     # return redirect(reverse('signup'))


#     # user = User.objects.get(email=details['email'])
#     # user.set_password(local_password)
#     # user.username = strategy.session_get('local_username', None)
#     # user.first_name = strategy.session_get('local_firstname', None)
#     # user.last_name = strategy.session_get('local_lastname', None)
#     # user.is_staff = True
#     # user.is_superuser = True
#     # user.save()

#     return # resume the pipeline
