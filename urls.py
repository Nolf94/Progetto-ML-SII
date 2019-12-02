# urls.py
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from lodreranker import views as views
from lodreranker import tests as test_views

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
    path('users/signup/books_form/', views.signup_s5, name='signup_s5'),
    path('users/signup/artists_form/', views.signup_s6, name='signup_s6'),
    path('users/signup/resume', views.route, name='resume'),
    path('users/profile', views.profile, name='profile'),
    path('users/social_disconnect/', views.social_disconnect, name='social_disconnect'),
    path('users/reset/', views.reset, name='reset'),
    path('users/logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('recommendation/', views.recommendation_view, name='recommendation'),
    path('recommendation/results', views.recommendation_results, name='recommendation_results'),

    # path('poi_recommendation_beta/results', views.recommendation_results, name='poi_recommendation_beta_results'),

    path('ajax/social_connect/', views.signup_s1_ajax, name='signup_s1_ajax'),
    path('ajax/recommendation/', views.recommendation_view_ajax, name='recommendation_view_ajax'),


    path('tests/clustering', test_views.test_clustering, name='test_clustering'),
]
