# lodreranker/auth_utils.py
from functools import wraps

from django.conf import settings
from django.shortcuts import render
from social_django.utils import load_strategy


def is_authenticated(user):
    if callable(user.is_authenticated):
        return user.is_authenticated()
    else:
        return user.is_authenticated

def associations(user, strategy):
    user_associations = strategy.storage.user.get_social_auth_for_user(user)
    if hasattr(user_associations, 'all'):
        user_associations = user_associations.all()
    return list(user_associations)

def common_context(authentication_backends, strategy, user=None, plus_id=None, **extra):
    """Common view context"""
    context = {
        'user': user,
        'available_backends': 'facebook',
        'associated': {}
    }
    
    if user and is_authenticated(user):
        context['associated'] = dict((association.provider, association) for association in associations(user, strategy))

    return dict(context, **extra)


def render_to(template):
    """Simple render_to decorator"""
    def decorator(func):
        """Decorator"""
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            """Rendering method"""
            out = func(request, *args, **kwargs) or {}
            if isinstance(out, dict):
                out = render(request, template, common_context(
                    settings.AUTHENTICATION_BACKENDS,
                    load_strategy(),
                    request.user,
                    plus_id=getattr(settings, 'SOCIAL_AUTH_GOOGLE_PLUS_KEY', None),
                    **out
                ))
            return out
        return wrapper
    return decorator
