# lodreranker/views.py
import json

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.staticfiles import finders
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, FormView, UpdateView
from social_django.models import UserSocialAuth

from .forms import CustomUserCreationForm, CustomUserDemographicDataForm
from .models import CustomUser
from .recommendation import ItemRanker, ItemRetriever, Recommender
from .usermodelbuilder import UserModelBuilder
from lodreranker import utils
from lodreranker import constants


def home(request):
    return render(request, 'home.html')


# Wrapper for social:begin to conditionally skip user social login if already existing.
def social_login(request):
    is_skip = request.GET.get('skip', False)
    request.session['skip_creation'] = True if is_skip else False
    return redirect(reverse('social:begin', args=('facebook',)))


# Recap user profile data and social data
# TODO show more fields 
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
    user.social_movies = None
    user.save()
    return redirect(reverse_lazy('profile'))


# Reset all user data
@login_required
def reset(request):
    user = request.user
    user.poi_weights = None
    user.has_poivector = False
    user.mov_weights = None
    user.has_movies = False
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
    profile = reverse_lazy('profile')

    if not user.has_social_connect:
        return redirect(s1)
    elif not user.has_demographic:
        return redirect(s2)
    elif not user.has_poivector:
        return redirect(s3)
    elif not user.has_movies:
        return redirect(s4)
    else:
        return redirect(profile)

# Handles user creation, automatically logins the new user after submit.
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


# Facebook connect, creates UserSocialAuth object.
@login_required
def signup_s1(request):
    template_name = 'registration/signup_s1.html'
    user = request.user
    if user.has_social_connect and user.has_social_data:
        return route(request)
    else:
        return render(request, template_name)

# Retrieve user media likes from UserSocialAuth.
@login_required
def signup_s1_ajax(request):
    user = request.user
    social_auth = UserSocialAuth.objects.filter(user=user.id)[0]

    retrieved_movies = ItemRetriever(constants.MOVIE).get_items_from_social(social_auth.extra_data['movies'])

    # TODO add many-to-many field for user

    # TODO remove social_movies from user
    user.social_movies = json.dumps(list(map(lambda x: x.tolist(), movies_vectors)))
    user.has_social_data = True
    user.save()
    return JsonResponse({'num_retrieved_movies': len(json.loads(user.social_movies))})    


# Demographic data form
class SignupS2View(LoginRequiredMixin, UpdateView):
    template_name = 'registration/signup_s2.html'
    form_class = CustomUserDemographicDataForm

    def get_object(self, queryset=None):
        return get_object_or_404(CustomUser, pk=self.request.user.id)

    def form_valid(self, form):
        user = self.request.user
        user.has_demographic = True
        user.save()
        return route(self.request)


# Helper function for cold-start form views.
### NB: this is not a view, don't access it directly in urls.py.
def handle_imgform(request, template_name, min_choices, session_obj_name, media_type):
    MIN_CHOICES = min_choices if min_choices else 5
    context = { 'min_choices': MIN_CHOICES }

    # choices are stored in session so that the random chosen order is kept during the process.
    if session_obj_name in request.session:
        choices = request.session[session_obj_name]
    else:
        # get a new random order
        choices = utils.get_image_choices(media_type)
        request.session[session_obj_name] = choices

    if request.method == 'POST':
        selected_images = []
        try:
            selected_images = list(request.POST.get('selected').split(','))
            if len(selected_images) < MIN_CHOICES:
                raise ValueError
        except ValueError:
            # keep choices in the next attempt
            context['error'] = True
            if selected_images:
                context['selected'] = ','.join(x for x in selected_images)
            return {'success': False, 'data': context}

        # clear the stored order
        request.session.pop(session_obj_name)
        request.session.modified = True
        return {'success': True, 'data': (selected_images, choices)}
    else:
        # load the form with the chosen random order
        return {'success': False, 'data': context}


# Cold-start form #1 (POI images)
@login_required
def signup_s3(request):
    template_name = 'registration/signup_s3.html'
    result = handle_imgform(request, template_name, 5, 'poi_choices', 'poi')
    if result['success']: 
        selected_images, poi_choices = result['data'][0], result['data'][1]
        vectors = utils.get_vectors_from_selection(selected_images, poi_choices)
        user = request.user
        user.has_poivector = True
        user.poi_weights = sum(vectors).tolist()
        user.save()
        return route(request)
    else:
        return render(request, template_name, result['data'])


# Cold-start form #2 (Movies)
@login_required
def signup_s4(request):
    template_name = 'registration/signup_s4.html'
    result = handle_imgform(request, template_name, 5, 'movie_choices', 'movies')
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


##### RECOMMENDATION
@login_required
def recommendation(request):
    template_name = 'recommendation.html'
    context = {'GOOGLE_MAPS_KEY': settings.GOOGLE_MAPS_KEY }

    if request.method == 'POST':
        coordinates = {
            'lat': request.POST.get('latitude'),
            'lng': request.POST.get('longitude'),
            'rad': request.POST.get('radius'),
        }

        user = request.user
        movie_recommender = Recommender(user, constants.MOVIE, coordinates, max_retrieved_items=30)
        
        # processo iterativo 
        retriever = movie_recommender.retriever
        retriever.retrieve_next()

        ranked_items = movie_recommender.recommend(type='clustering')
        context['ranked_items'] = list(map(lambda x: x['name'], ranked_items))

    return render(request, template_name, context)

@login_required
def recommendation_summarize_result(request):
    template_name = 'recommendation.html'
    context = {'GOOGLE_MAPS_KEY': settings.GOOGLE_MAPS_KEY }

    if request.method == 'POST':
        lat = request.POST.get('latitude')
        lng  = request.POST.get('longitude')
        rad  = request.POST.get('radius')
        print(f'[{lat}, {lng}, {rad}]')
    
        user = request.user
        movie_vectors = json.loads(user.form_movies)
        for vec in json.loads(user.social_movies):
            if vec not in movie_vectors:
                movie_vectors.append(vec)

        movie_sum = UserModelBuilder().build_summarize_model(movie_vectors)
        print(movie_sum)

        geo_items = UserModelBuilder().get_items_from_coordinates(lat, lng, rad, constants.MOVIE)
        ranked_items = ItemRanker().rank_summarize_items(movie_sum, geo_items)
        context['ranked_items'] = list(map(lambda x: x['name'], ranked_items))

    return render(request, template_name, context)
