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
            return redirect(reverse_lazy('profile'))
        else:
            # TODO add a parameter to render the error in the login page
            from pprint import pprint
            import inspect
            # pprint(dir(strategy))
            strategy.session_set('not_existing', True)
            return redirect(reverse_lazy('login')) 
    else:
        return # continue the pipeline


def redirect_registration(strategy, backend, user, response, *args, **kwargs):
    # UNUSED
    # user.social_uid = kwargs['uid']
    user.has_social_connect = True
    user.save()
    return redirect(reverse_lazy('signup_s1'))
