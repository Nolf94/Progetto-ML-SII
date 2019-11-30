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

    def get_info(mtype):
        return list(map(lambda x: f'{x.name}  ({x.wkd_id}, {len(x.abstract)} chars.)', user.social_items.filter(media_type=mtype)))

    # TODO improve context variables 
    can_disconnect = (user.social_auth.count() > 1 or user.has_usable_password())
    return render(request, 'profile.html', {
        'facebook_login': facebook_login,
        'can_disconnect': can_disconnect,
        f'{constants.MOVIE}': get_info(constants.MOVIE),
        f'{constants.BOOK}': get_info(constants.BOOK),
        f'{constants.MUSIC}': get_info(constants.MUSIC),
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
        session = request.session
        if 'retriever' in session.keys():
            request.session.pop('retriever')
        if 'list_mediatype' in session.keys():
            request.session.pop('list_mediatype')
        return render(request, template_name)

# Retrieve user media likes from UserSocialAuth.
@login_required
@csrf_exempt
def signup_s1_ajax(request):
    user = request.user
    social_auth = UserSocialAuth.objects.filter(user=user.id)[0]

    if request.is_ajax():
        session = request.session
        if 'mtypes' in session.keys():
            if request.POST.get('next_mtype'):
                session['mtypes'].pop(0)
                if not session['mtypes']:
                    session.pop('mtypes')
                    return JsonResponse({'retrieval_done': True})
        else:
            session['mtypes'] = [ constants.MOVIE, constants.BOOK, constants.MUSIC ]

        if 'retriever' in session.keys():
            retriever = jsonpickle.decode(session['retriever'])
            retriever.retrieve_next()
        else:
            mediatype = session['mtypes'][0]
            retriever = SocialItemRetriever(mediatype)
            retriever.initialize(social_auth.extra_data[mediatype])

        encoded_retriever = jsonpickle.encode(retriever)
        session['retriever'] = encoded_retriever

        if not retriever.next:
            for itemid in retriever.retrieved_items:
                user.social_items.add(RetrievedItem.objects.get(wkd_id=itemid))
            user.has_social_data = True
            user.save()
            session.pop('retriever')

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

    session = request.session
    if request.method == 'POST':
        context['ajax_begin']  = True
        area = utils.GeoArea(
            request.POST.get('latitude'),
            request.POST.get('longitude'),
            request.POST.get('radius')
        )
        session['area'] = jsonpickle.encode(area)
        if 'retriever' in session.keys():
            session.pop('retriever')
        if 'retriever' in session.keys():
            session.pop('retriever_name')
        if 'list_mediatype' in session.keys():
            session.pop('list_mediatype')
        if 'results' in session.keys():
            session.pop('results')

    return render(request, template_name, context)

@login_required
@csrf_exempt
def recommendation_view_ajax(request):
    user = request.user

    if request.is_ajax():
        session = request.session

        if 'mtypes' in session.keys():
            if request.POST.get('next_mtype'):
                session['mtypes'].pop(0)
                if not session['mtypes']:
                    session.pop('mtypes')
                    session.pop('area')
                    return JsonResponse({'retrieval_done': True})
        else:
            session['mtypes'] = [constants.MOVIE, constants.BOOK, constants.MUSIC]
            # session['mtypes'] = [constants.MOVIE]

        if 'retriever' in session.keys():
            retriever = jsonpickle.decode(session['retriever'])
            retriever.retrieve_next()
        else:
            mediatype = session['mtypes'][0]
            retriever = GeoItemRetriever(mediatype, limit=15)
            if 'area' in session.keys():
                area = jsonpickle.decode(session['area'])
            retriever.initialize(area)

        encoded_retriever = jsonpickle.encode(retriever)
        session['retriever'] = encoded_retriever

        if not retriever.next:
            session.pop('retriever')
            session['retriever_name'] = type(retriever).__name__
            recommender = Recommender(retriever.mtype, user, retriever)

            mtype_results = {}
            try:
                for method in constants.METHODS:
                    mtype_results[method] = recommender.recommend(method=method, strip=True)
                # mtype_results = {
                #     'clustering': recommender.recommend(method='clustering', strip=True),
                #     'summarize': recommender.recommend(method='summarize', strip=True),
                #     'outdegree': recommender.recommend(method='outdegree', strip=True),
                # }
            except utils.RetrievalError:
                # mtype_results will be empty
                pass

            if 'results' in session.keys():
                session['results'][retriever.mtype] = mtype_results
            else:
                session['results'] = {retriever.mtype: mtype_results}
            session[f'results_{retriever.mtype}'] = mtype_results

    return JsonResponse(json.loads(encoded_retriever))


@login_required
def recommendation_results(request):
    template_name = 'results.html'
    context = {}
    session = request.session

    # if request.method == 'GET':
    if 'results' in session.keys():
        results = session['results']
    else: 
        return redirect(reverse_lazy('recommendation'))

    items = {}
    for mtype, mtype_data in results.items():
        if mtype_data:
            itemids = list(set([el['id'] for ranking in mtype_data.values() for el in ranking]))
            try:
                mtype_items = [RetrievedItem.objects.get(wkd_id=itemid) for itemid in itemids]
            
                items.update( [(item.wkd_id, item.__dict__) for item in mtype_items] )
            
            except RetrievedItem.DoesNotExist:
                return # it should never ever fire
            
    # results['movies'] = {} 
    # results['books'] = results['movies']
    # results['artists'] = {}
    context['has_results'] = any([results[x] for x in results.keys()])
    context['results'] = results
    context['items'] = items   


    beyondaccuracy_text = {
        'rating': 'multimedia content that matched my interests',
        'novelty': 'multimedia content that I did not know before',
        'serendipity': 'surprisingly interesting multimedia content that I might not have known in other ways',
        'diversity': 'multimedia content that are different to each other(among content of the same type)',
    }
    context['beyondaccuracy'] = beyondaccuracy_text


    # else:

    if request.method == 'POST':
        post_dict = request.POST
        print(session['retriever_name'])
        for key in filter(lambda x: x.startswith('ranking'), post_dict.keys()):
            print(key)


        # handle evaluation

    return render(request, template_name, context)
