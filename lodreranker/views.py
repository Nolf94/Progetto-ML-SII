# lodreranker/views.py
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.staticfiles import finders
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, FormView, UpdateView
from social_django.models import UserSocialAuth
from .forms import CustomUserCreationForm, CustomUserDemographicDataForm
from .misc import *
from .models import CustomUser
from .utils import get_choices, get_poi_weights, get_wikipedia_abstract, get_like_vectors, get_vectors


def home(request):
    return render(request, 'home.html')


# wrapper for social:begin to conditionally skip user social login if already existing.
def social_login(request):
    is_skip = request.GET.get('skip', False)
    request.session['skip_creation'] = True if is_skip else False
    return redirect(reverse('social:begin', args=('facebook',)))


# handles user creation. automatically logins the new user after submit.
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


# user social auth creation (connect to facebook)
@login_required
def signup_s1(request):
    template_name = 'registration/signup_s1.html'
    return render(request, template_name)


# updates user profile with demographic data
# TODO add new fields (geolocalization?)
class SignupS2View(LoginRequiredMixin, UpdateView):
    template_name = 'registration/signup_s2.html'
    form_class = CustomUserDemographicDataForm
    success_url = reverse_lazy('signup_s3')

    def get_object(self, queryset=None):
        return get_object_or_404(CustomUser, pk=self.request.user.id)

    def render_to_response(self, context, **response_kwargs):
        user = self.request.user
        user.has_demographic = True
        user.save()
        return super().render_to_response(context, **response_kwargs)


# cold-start form #1 (POI images)
@login_required
def signup_s3(request):
    template_name = 'registration/signup_s3.html'
    MIN_CHOICES = 5

    # choices are stored in session so that the random chosen order is kept during the process.
    session = request.session
    if 'choices' in session:
        poi_choices = session['choices']
    else:
        poi_choices = get_choices('poi')
        session['choices'] = poi_choices

    context = {
        'min_choices': MIN_CHOICES
    }
   
    if request.method == 'POST':
        selected_images = []
        try:
            selected_images = list(request.POST.get('selected').split(','))
            if len(selected_images) < MIN_CHOICES:
                raise ValueError
        except ValueError:
            context['error'] = True
            if selected_images:
                context['selected'] = ','.join(x for x in selected_images)
            return render(request, template_name, context)
            
        weights = get_poi_weights(selected_images, poi_choices)
        user = request.user
        user.has_poivector = True
        user.poi_weights = weights
        user.save()
        session.pop('choices')
        session.modified = True
        return redirect(reverse_lazy('signup_s4'))
    else:
        return render(request, template_name, context)


# cold-start form #2 (Movies)
@login_required
def signup_s4(request):
    template_name = 'registration/signup_s4.html'
    MIN_CHOICES = 5

    # choices are stored in session so that the random chosen order is kept during the process.
    session = request.session
    if 'm_choices' in session:
        movie_choices = session['m_choices']
    else:
        movie_choices = get_choices('movies')
        session['m_choices'] = movie_choices

    context = {
        'min_choices': MIN_CHOICES,
    }
   
    if request.method == 'POST':
        selected_images = []
        try:
            selected_images = list(request.POST.get('selected').split(','))
            if len(selected_images) < MIN_CHOICES:
                raise ValueError
        except ValueError:
            context['error'] = True
            if selected_images:
                context['selected'] = ','.join(x for x in selected_images)
            return render(request, template_name, context)


        # ########## TODO vector clustering (including social data vectors, maybe move code to another script)
        # weights = get_poi_weights(selected_images, movie_choices)
        user = request.user
        user.has_movvector = True
        # user.poi_weights = weights
        user.save()

        
        session.pop('m_choices')
        session.modified = True
        return redirect(reverse_lazy('profile'))
    else:
        return render(request, template_name, context)


# recap user profile data and social data
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


# handle Facebook disconnect and disassociate social auth from user
@login_required
def social_disconnect(request):
    user = request.user
    soc_auths = UserSocialAuth.objects.filter(user=user.id)[0].delete()  
    user.has_social = False
    user.save()
    return redirect(reverse_lazy('profile'))


@login_required
def reset(request):
    user = request.user
    user.poi_weights = None
    user.has_poivector = False
    user.mov_weights = None
    user.has_movvector = False
    for name in {f.name: None for f in user._meta.fields if f.null}:
        setattr(user, name, None)
    user.has_demographic = False
    user.save()
    return redirect(reverse_lazy('social_disconnect'))



@login_required
def test(request):
    user = request.user
    social_auth = UserSocialAuth.objects.filter(user=user.id)[0]

    # print(social_auth.extra_data.keys())
    from pprint import pprint
    pprint(social_auth.extra_data['movies'])

    ####### TODO improve abstract retrieval (see utils.py)
    print(get_like_vectors(social_auth.extra_data["movies"]["data"]))
    return redirect(reverse_lazy('profile'))
