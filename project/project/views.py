from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.urls import reverse_lazy
from facepy import SignedRequest
from facepy.exceptions import SignedRequestError
import urllib.request, json 
from social_django.models import UserSocialAuth
import requests

class AboutView(LoginRequiredMixin, TemplateView):
    template_name="about.html"
    login_url = reverse_lazy('social:begin', args=['facebook'])

    def get_context_data(self, **kwargs):
        context = super(AboutView, self).get_context_data(**kwargs)
        s_user = self.request.user.social_auth.get(provider='facebook')
        access_token = s_user.extra_data['access_token']
        context['avatar_url'] = f'https://graph.facebook.com/{s_user.uid}/picture?type=large'
        #url = requests.get(f' https://graph.facebook.com/me?fields=books.limit(99999).summary(true)&access_token={access_token}')
        #url = requests.get(f' https://graph.facebook.com/me?fields=movies.limit(99999).summary(true)&access_token={access_token}')
        url = requests.get(f' https://graph.facebook.com/me?fields=music.limit(99999).summary(true)&access_token={access_token}')
        #url = requests.get(f' https://graph.facebook.com/me?fields=albums.fields(photos.limit(99999).fields(alt_text))&limit=99999&access_token={access_token}')
        #url = requests.get(f' https://graph.facebook.com/me?fields=posts.fields(description).limit(99999)&access_token={access_token}')
        likes = url.json
        context['likes'] = likes
        return context


class IndexView(TemplateView):
        template_name="index.html"

class DeauthorizeView(View):
    def post(self, request, *args, **kwargs):
        try:
            signed_request = request.POST['signed_request']
        except (KeyError):
            return HttpResponse(status=400, content='Invalid request')
        try:
            signed_request_data = SignedRequest.parse(
                signed_request,
                settings.SOCIAL_AUTH_FACEBOOK_SECRET
            )
        except (SignedRequestError):
            return HttpResponse(status=400, content='Invalid request')
        user_id = signed_request_data['user_id']
        try:
            user = UserSocialAuth.objects.get(uid=user_id, provider=facebook).user
        except(UserSocialAuth.DoesNotExist):
            return HttpResponse(status=400, content='Invalid request')
        user.update(is_active=False)
        return HttpResponse(status=201)
