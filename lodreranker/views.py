# lodreranker/views.py
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, reverse
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from social_django.utils import load_strategy

from .forms import CreatePasswordForm, CustomUserCreationForm, CustomUserDemographicDataForm
from .misc import *


def home(request):
    return render(request, 'home.html')


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

def signup_s1(request):
    template_name = 'registration/signup_s1.html'
    return render(request, template_name)

class SignupS2View(CreateView):
    template_name = 'registration/signup_s2.html'
    form_class = CustomUserDemographicDataForm

    # def form_valid(self, form):
    #     form.save()
    #     username = self.request.POST['username']
    #     password = self.request.POST['password1']
    #     user = authenticate(username=username, password=password)
    #     login(self.request, user)
    #     return redirect(reverse_lazy('signup_s1'))








# def s0_createpassword(request):
#     if request.method == 'POST':
#         form = CreatePasswordForm(request.POST)
#         if form.is_valid():
#             request.session['local_password'] = form.cleaned_data['password']
#             return redirect(reverse('social:complete', args=('facebook',)))
#     else:
#         form = CreatePasswordForm()

#     return render(request, "signup_s0_createpassword.html", {'form': form})












# import json
# import urllib.request
# from django.http.response import Http404
# from django.conf import settings
# from django.contrib.auth.models import User
# from django.urls import reverse_lazy
# from django.views.generic import TemplateView, View
# from facepy import SignedRequest
# from facepy.exceptions import SignedRequestError
# from social_django.models import UserSocialAuth





# UNUSED
# class AboutView(LoginRequiredMixin, TemplateView):
    # template_name = "about.html"
    # login_url = reverse_lazy('social:begin', args=['facebook'])

    # def get_context_data(self, **kwargs):
        # context = super(AboutView, self).get_context_data(**kwargs)
        # s_user = self.request.user.social_auth.get(provider='facebook')
        # access_token = s_user.extra_data['access_token']

        # context['avatar_url'] = f'https://graph.facebook.com/{s_user.uid}/picture?type=large'


        # FB_QUERIES = {
        #     'feed': f'https://graph.facebook.com/me?fields=feed.limit(99999)&access_token=',
        #     'posts': f'https://graph.facebook.com/me?fields=feed.limit(99999)&access_token=',
        #     'likes': f'https://graph.facebook.com/me?fields=likes.limit(99999).summary(true)&access_token=',
        #     'movies': f'https://graph.facebook.com/me?fields=movies.limit(99999)&access_token=',
        #     'books': f'https://graph.facebook.com/me?fields=likes.limit(99999).summary(true)&access_token=',
        #     'albums': f'https://graph.facebook.com/me?fields=albums.fields(photos.limit(99999).fields(alt_text))&limit=99999&access_token=',
        #     'music': f'https://graph.facebook.com/me?fields=music.limit(99999)&access_token=',
        # }

        # # fb_query = FB_QUERIES['feed'] + access_token
        # # context['fbdata'] = requests.get(fb_query).json

"""
film = "the amazing spider-man 2"
abstract = misc.Lod_queries.retrieveFilmAbstract(film)
context['querydata'] = abstract
"""

        # return context


# UNUSED
# class DeauthorizeView(View):
#     def post(self, request, *args, **kwargs):
#         try:
#             signed_request = request.POST['signed_request']
#         except (KeyError):
#             return Http404(status=400, content='Invalid request')
#         try:
#             signed_request_data = SignedRequest.parse(
#                 signed_request,
#                 settings.SOCIAL_AUTH_FACEBOOK_SECRET
#             )
#         except (SignedRequestError):
#             return Http404(status=400, content='Invalid request')
#         user_id = signed_request_data['user_id']
#         try:
#             user = UserSocialAuth.objects.get(uid=user_id, provider='facebook').user
#         except(UserSocialAuth.DoesNotExist):
#             return Http404(status=400, content='Invalid request')
#         user.update(is_active=False)
#         return Http404(status=201)
