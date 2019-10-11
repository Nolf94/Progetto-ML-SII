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
    path('users/signup/connect_social', core_views.signup_s1, name='signup_s1'),
    path('users/signup/demographic_data/', core_views.SignupS2View.as_view(), name='signup_s2'),
    path('users/signup/images_form/', core_views.signup_s3, name='signup_s3'),
    path('users/settings/', core_views.settings, name='settings'),

    path('users/signup/social-auth/', include('social_django.urls', namespace='social')),
    path('users/logout/', auth_views.LogoutView.as_view(), name='logout'),
    # path('user/', core_views.userdata, name='userdata'),
]