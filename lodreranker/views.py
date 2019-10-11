# lodreranker/views.py
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from social_django.models import UserSocialAuth
from social_django.utils import load_strategy

from .forms import CreatePasswordForm, CustomUserCreationForm, CustomUserDemographicDataForm
from .misc import *
from .models import CustomUser


def home(request):
    return render(request, 'home.html')


def social_login(request):
    is_skip = request.GET.get('skip', False)
    request.session['skip_creation'] = True if is_skip else False
    return redirect(reverse('social:begin', args=('facebook',)))


class SignupS0View(CreateView):
    template_name = 'registration/signup_s0.html'
    form_class = CustomUserCreationForm

    def form_valid(self, form):
        form.save() 
        username = self.request.POST['username']
        password = self.request.POST['password1']
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return redirect(reverse_lazy('signup_s1'))

@login_required
def signup_s1(request):
    template_name = 'registration/signup_s1.html'
    return render(request, template_name)


class SignupS2View(LoginRequiredMixin, UpdateView):
    template_name = 'registration/signup_s2.html'
    form_class = CustomUserDemographicDataForm
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        return get_object_or_404(CustomUser, pk=self.request.user.id)

    def render_to_response(self, context, **response_kwargs):
        user = self.request.user
        user.has_demographic = True
        user.save()
        return super().render_to_response(context, **response_kwargs)

def signup_s3(request):
    return redirect(reverse('home'))


@login_required
def settings(request):
    user = request.user
    
    try:
        facebook_login = user.social_auth.get(provider='facebook')
    except UserSocialAuth.DoesNotExist:
        facebook_login = None
    
    can_disconnect = (user.social_auth.count() > 1 or user.has_usable_password())
    return render(request, '/settings.html', {
        'facebook_login': facebook_login,
        'can_disconnect': can_disconnect
    })




# FB_QUERIES = {
#     'feed': f'https://graph.facebook.com/me?fields=feed.limit(99999)&access_token=',
#     'posts': f'https://graph.facebook.com/me?fields=feed.limit(99999)&access_token=',
#     'likes': f'https://graph.facebook.com/me?fields=likes.limit(99999).summary(true)&access_token=',
#     'movies': f'https://graph.facebook.com/me?fields=movies.limit(99999)&access_token=',
#     'books': f'https://graph.facebook.com/me?fields=likes.limit(99999).summary(true)&access_token=',
#     'albums': f'https://graph.facebook.com/me?fields=albums.fields(photos.limit(99999).fields(alt_text))&limit=99999&access_token=',
#     'music': f'https://graph.facebook.com/me?fields=music.limit(99999)&access_token=',
# }
"""
film = "the amazing spider-man 2"
abstract = misc.Lod_queries.retrieveFilmAbstract(film)
context['querydata'] = abstract
"""