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

from lodreranker import constants, forms, models, recommendation, utils

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
    # elif not user.has_poivector:
        # return redirect(s3)
    elif not user.has_movies:
        return redirect(s4)
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
        from pprint import pprint

        pprint(session.keys())
        if 'retriever' in session.keys():
            retriever = jsonpickle.decode(session['retriever'])
            retriever.retrieve_next()
        else:
            retriever = recommendation.SocialItemRetriever(constants.MOVIE)
            retriever.initialize(social_auth.extra_data['movies'])

        encoded_retriever = jsonpickle.encode(retriever)
        session['retriever'] = encoded_retriever

        if not retriever.next:
            for itemid in retriever.retrieved_items:
                user.social_items.add(models.RetrievedItem.objects.get(wkd_id=itemid))
            user.has_social_data = True
            user.save()
        
        # OLD BULK METHOD
        # social_movies = ItemRetriever(constants.MOVIE).retrieve_from_social(social_auth.extra_data['movies'])
        # user.social_items.add(*social_movies)


    # return JsonResponse({'num_retrieved_movies': len(social_movies)})    
    return JsonResponse(json.loads(encoded_retriever))    


# Demographic data form
class SignupS2View(LoginRequiredMixin, UpdateView):
    template_name = 'registration/signup_s2.html'
    form_class = forms.CustomUserDemographicDataForm

    def get_object(self, queryset=None):
        return get_object_or_404(models.CustomUser, pk=self.request.user.id)

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


##### RECOMMENDATION
@login_required
def recommendation_view(request):
    template_name = 'recommendation.html'
    context = {'GOOGLE_MAPS_KEY': settings.GOOGLE_MAPS_KEY }

    if request.method == 'POST':
        area = utils.GeoArea(
            request.POST.get('latitude'),
            request.POST.get('longitude'),
            request.POST.get('radius')
        )
        user = request.user
        movie_recommender = recommendation.Recommender(user, constants.MOVIE, max_retrieved_items=30)
        
        # bulk load 
        retriever = movie_recommender.retriever
        retriever.retrieve_from_geoarea(area)

        # TODO retriever.retrieve_next()

        ranked_items = movie_recommender.recommend(constants.MOVIE, method='clustering')
        ranked_items_2 = movie_recommender.recommend(constants.MOVIE, method='summarize')
        context['ranked_items'] = list(map(lambda x: x['name'], ranked_items))
        context['ranked_items_2'] = list(map(lambda x: x['name'], ranked_items_2))

    return render(request, template_name, context)
