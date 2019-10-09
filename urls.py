# urls.py
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from lodreranker import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),     
    path('', core_views.home, name='home'),
    
    path('users/', include('django.contrib.auth.urls')),
    path('users/signup/', core_views.SignUpView.as_view(), name='signup'),
    path('users/signup/s0', core_views.s0_createpassword, name='s0_createpassword'),
    path('users/signup/s1', core_views.s1_additionaldata, name='s1_additionaldata'),
    path('users/logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('users/social-auth/', include('social_django.urls', namespace='social')),
    # path('user/', core_views.userdata, name='userdata'),
]
