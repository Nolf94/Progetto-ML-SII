# urls.py
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from lodreranker import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),     
    path('', core_views.home, name='home'),
    
    path('users/', include('django.contrib.auth.urls')),
    path('users/social_login', core_views.social_login, name='social_login'),
    path('users/signup/', core_views.SignupS0View.as_view(), name='signup'),
    path('users/signup/social_connect', core_views.signup_s1, name='signup_s1'),
    path('users/signup/demographic_data/', core_views.SignupS2View.as_view(), name='signup_s2'),
    path('users/signup/images_form/', core_views.signup_s3, name='signup_s3'),
    path('users/signup/movies_form/', core_views.signup_s4, name='signup_s4'),
    path('users/profile', core_views.profile, name='profile'),
    path('users/social_disconnect/', core_views.social_disconnect, name='social_disconnect'),\


    path('test/', core_views.test, name='test'),
    

    path('users/signup/social-auth/', include('social_django.urls', namespace='social')),
    path('users/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('users/reset/', core_views.reset, name='reset'),

]