import json
import urllib.request

from django.http.response import Http404
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View
from facepy import SignedRequest
from facepy.exceptions import SignedRequestError
from social_django.models import UserSocialAuth

from . import misc


def login(request):
    return render(request, 'login.html')

@login_required
def userdata(request):
    return render(request, 'userdata.html')


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
# class IndexView(TemplateView):
#     template_name = "index.html"

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
