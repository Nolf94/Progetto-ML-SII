# lodreranker/views.py
import json

import jsonpickle
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.staticfiles import finders
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, FormView, UpdateView
from social_django.models import UserSocialAuth

from lodreranker import constants, forms, utils
from lodreranker.models import CustomUser, RetrievedItem
from lodreranker.recommendation import (ItemRanker, GeoItemRetriever, Recommender,
                                        SocialItemRetriever)


def home(request):
    return render(request, 'home.html')


# Wrapper for social:begin to conditionally skip user social login if already existing.
def social_login(request):
    is_skip = request.GET.get('skip', False)
    request.session['skip_creation'] = True if is_skip else False
    return redirect(reverse('social:begin', args=('facebook',)))


# Recap user profile data and social data
# TODO add more fields (profession)
@login_required
def profile(request):
    user = request.user
    try:
        facebook_login = user.social_auth.get(provider='facebook')
    except UserSocialAuth.DoesNotExist:
        facebook_login = None

    can_disconnect = (user.social_auth.count() > 1 or user.has_usable_password())
    return render(request, 'profile.html', {
        'facebook_login': facebook_login,
        'can_disconnect': can_disconnect
    })


# Handle Facebook disconnect and disassociate social auth from user
@login_required
def social_disconnect(request):
    user = request.user
    soc_auths = UserSocialAuth.objects.filter(user=user.id)[0].delete()
    user.has_social_connect = False
    user.has_social_data = False
    user.social_items.clear()
    user.save()
    return redirect(reverse_lazy('profile'))
    # return redirect(reverse_lazy('signup_s1'))


# Reset all user data
@login_required
def reset(request):
    user = request.user
    # user.poi_weights = None
    # user.has_poivector = False
    user.form_movies = None
    user.form_books = None
    user.form_artists = None
    user.has_movies = False
    user.has_books = False
    user.has_artists = False
    for name in {f.name: None for f in user._meta.fields if f.null}:
        setattr(user, name, None)
    user.has_demographic = False
    user.save()
    return redirect(reverse_lazy('social_disconnect'))


# Helper view for signup pipeline
def route(request):
    user = request.user
    s1 = reverse_lazy('signup_s1')
    s2 = reverse_lazy('signup_s2')
    s3 = reverse_lazy('signup_s3')
    s4 = reverse_lazy('signup_s4')
    s5 = reverse_lazy('signup_s5')
    s6 = reverse_lazy('signup_s6')
    profile = reverse_lazy('profile')

    if not user.has_social_connect:
        return redirect(s1)
    elif not user.has_demographic:
        return redirect(s2)
    # elif not user.has_poivector:
        # return redirect(s3)
    elif not user.has_movies:
        return redirect(s4)
    elif not user.has_books:
        return redirect(s5)
    elif not user.has_artists:
        return redirect(s6)
    else:
        return redirect(profile)

# Handles user creation, automatically logins the new user after submit.
class SignupS0View(CreateView):
    template_name = 'registration/signup_s0.html'
    form_class = forms.CustomUserCreationForm

    def form_valid(self, form):
        form.save()
        username = self.request.POST['username']
        password = self.request.POST['password1']
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return redirect(reverse_lazy('signup_s1'))


# Facebook connect, creates UserSocialAuth object.
@login_required
def signup_s1(request):
    template_name = 'registration/signup_s1.html'
    user = request.user
    if user.has_social_connect and user.has_social_data:
        return route(request)
    else:
        try:
            request.session.pop('retriever')
        except:
            pass
        return render(request, template_name)

# Retrieve user media likes from UserSocialAuth.
@login_required
@csrf_exempt
def signup_s1_ajax(request):
    user = request.user
    social_auth = UserSocialAuth.objects.filter(user=user.id)[0]

    if request.is_ajax():
        session = request.session

        if 'retriever' in session.keys():
            retriever = jsonpickle.decode(session['retriever'])
            retriever.retrieve_next()
        else:
            retriever = SocialItemRetriever(constants.MUSIC)
            retriever.initialize(social_auth.extra_data['music'])
            # retriever = SocialItemRetriever(constants.MOVIE)
            # retriever.initialize(social_auth.extra_data['movies'])

        encoded_retriever = jsonpickle.encode(retriever)
        session['retriever'] = encoded_retriever

        if not retriever.next:
            for itemid in retriever.retrieved_items:
                user.social_items.add(RetrievedItem.objects.get(wkd_id=itemid))
            user.has_social_data = True
            user.save()
    return JsonResponse(json.loads(encoded_retriever))


# Demographic data form
class SignupS2View(LoginRequiredMixin, UpdateView):
    template_name = 'registration/signup_s2.html'
    form_class = forms.CustomUserDemographicDataForm

    def get_object(self, queryset=None):
        return get_object_or_404(CustomUser, pk=self.request.user.id)

    def form_valid(self, form):
        user = self.request.user
        user.has_demographic = True
        user.save()
        return route(self.request)


# Cold-start form #1 (POIs)
@login_required
def signup_s3(request):
    """POI FORM IS DISABLED"""
    return redirect(reverse_lazy('profile'))
    # template_name = 'registration/signup_s3.html'
    # result = utils.handle_imgform(request, template_name, 5, 'poi_choices', 'poi')
    # if result['success']:
    #     selected_images, poi_choices = result['data'][0], result['data'][1]
    #     vectors = utils.get_vectors_from_selection(selected_images, poi_choices)
    #     user = request.user
    #     user.has_poivector = True
    #     user.poi_weights = sum(vectors).tolist()
    #     user.save()
    #     return route(request)
    # else:
    #     return render(request, template_name, result['data'])


# Cold-start form #2 (Movies)
@login_required
def signup_s4(request):
    template_name = 'registration/signup_s4.html'
    result = utils.handle_imgform(request, template_name, 5, 'movie_choices', 'movies')
    if result['success']:
        selected_images, movie_choices = result['data'][0], result['data'][1]
        user = request.user
        movies_vectors = utils.get_vectors_from_selection(selected_images, movie_choices)
        user.form_movies = json.dumps(list(map(lambda x: x.tolist(), movies_vectors)))
        user.has_movies = True
        user.save()
        return route(request)
    else:
        return render(request, template_name, result['data'])


# Cold-start form #3 (Books)
@login_required
def signup_s5(request):
    template_name = 'registration/signup_s5.html'
    result = utils.handle_imgform(request, template_name, 5, 'book_choices', 'books')
    if result['success']:
        selected_images, book_choices = result['data'][0], result['data'][1]
        user = request.user
        books_vectors = utils.get_vectors_from_selection(selected_images, book_choices)
        user.form_books = json.dumps(list(map(lambda x: x.tolist(), books_vectors)))
        user.has_books = True
        user.save()
        return route(request)
    else:
        return render(request, template_name, result['data'])


# Cold-start form #4 (Artists)
@login_required
def signup_s6(request):
    template_name = 'registration/signup_s6.html'
    result = utils.handle_imgform(request, template_name, 5, 'artist_choices', 'artists')
    if result['success']:
        selected_images, artist_choices = result['data'][0], result['data'][1]
        user = request.user
        artists_vectors = utils.get_vectors_from_selection(selected_images, artist_choices)
        user.form_artists = json.dumps(list(map(lambda x: x.tolist(), artists_vectors)))
        user.has_artists = True
        user.save()
        return route(request)
    else:
        return render(request, template_name, result['data'])


##### RECOMMENDATION
@login_required
def recommendation_view(request):
    template_name = 'recommendation.html'
    context = {'GOOGLE_MAPS_KEY': settings.GOOGLE_MAPS_KEY }

    if request.method == 'POST':
        context['ajax_begin']  = True
        area = utils.GeoArea(
            request.POST.get('latitude'),
            request.POST.get('longitude'),
            request.POST.get('radius')
        )
        request.session['area'] = jsonpickle.encode(area)
        try:
            request.session.pop('retriever')
        except:
            pass
    return render(request, template_name, context)


@login_required
@csrf_exempt
def recommendation_view_ajax(request):
    user = request.user

    if request.is_ajax():
        session = request.session

        if 'area' in session.keys():
            area = jsonpickle.decode(session['area'])
            session.pop('area')

        if 'retriever' in session.keys():
            retriever = jsonpickle.decode(session['retriever'])
            retriever.retrieve_next()
        else:
            retriever = GeoItemRetriever(constants.MOVIE, sparql_limit=10)
            try:
                retriever.initialize(area)
            except utils.RetrievalError:
                return # TODO exception handling

        encoded_retriever = jsonpickle.encode(retriever)
        session['retriever'] = encoded_retriever

        if not retriever.next:
            pass
            # TODO RESTORE RECOMMENDATION

            # movie_recommender = Recommender(constants.MOVIE, user, movie_retriever)
            # try:
            #     ranking_clustering = movie_recommender.recommend(method='clustering')
            #     ranking_summarize = movie_recommender.recommend(method='summarize')
            #     context['itemsfound'] = True
            #     context['ranking_clustering'] = list(map(lambda x: x['item'].name, ranking_clustering))
            #     context['ranking_summarize'] = list(map(lambda x: x['item'].name, ranking_summarize))

            # except utils.RetrievalError:
            #     context['itemsfound'] = False
            
    return JsonResponse(json.loads(encoded_retriever))