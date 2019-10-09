from django.shortcuts import redirect, reverse
from .models import CustomUser
from social_core.pipeline.partial import partial

from pprint import pprint

@partial
def s0(strategy, backend, request, details, *args, **kwargs):
    local_password = strategy.session_get('local_password', None)
    if not local_password:
        return redirect(reverse('s0_createpassword'))

    user = CustomUser.objects.get(id=kwargs['user'].id)
    user.set_password(local_password)
    user.save()

    return


@partial
def s1(strategy, backend, request, details, *args, **kwargs):
    ok = strategy.session_get('ok', None)

    if not ok:
        return redirect(reverse('s1_additionaldata'))
    
    return



####################################################################################################




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
