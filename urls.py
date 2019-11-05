# urls.py
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from lodreranker import views as views

urlpatterns = [
    path('admin/', admin.site.urls),     
    path('', views.home, name='home'),
    
    path('users/', include('django.contrib.auth.urls')),
    path('users/social_login', views.social_login, name='social_login'),
    path('users/signup/', views.SignupS0View.as_view(), name='signup'),
    path('users/signup/social_connect', views.signup_s1, name='signup_s1'),
    path('users/signup/social-auth/', include('social_django.urls', namespace='social')),
    path('users/signup/demographic_data/', views.SignupS2View.as_view(), name='signup_s2'),
    path('users/signup/images_form/', views.signup_s3, name='signup_s3'),
    path('users/signup/movies_form/', views.signup_s4, name='signup_s4'),
    path('users/signup/resume', views.route, name='resume'),
    path('users/profile', views.profile, name='profile'),
    path('users/social_disconnect/', views.social_disconnect, name='social_disconnect'),
    path('users/reset/', views.reset, name='reset'),
    path('users/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('ajax/social_connect/get_movie_likes', views.signup_s1_ajax, name='signup_s1_ajax'),

    path('recommendation/simple/', views.recommend_simple, name='recommend_simple'),
]