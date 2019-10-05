import os
from pathlib import Path
from django.urls import reverse_lazy
from dotenv import load_dotenv

try:
    env_path = Path('.', 'env.config').resolve()
except:
    raise Exception("[BGM] Please provide a valid .env file")

load_dotenv(dotenv_path=env_path, verbose=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1'
]

INSTALLED_APPS = [
    'lodreranker',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social_django',
    'sslserver'
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.security.SecurityMiddleware',
]

ROOT_URLCONF = 'urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'
AUTHENTICATION_BACKENDS = (
    'social_core.backends.facebook.FacebookOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_FACEBOOK_KEY = os.getenv("SOCIAL_AUTH_FACEBOOK_KEY")
SOCIAL_AUTH_FACEBOOK_SECRET = os.getenv("SOCIAL_AUTH_FACEBOOK_SECRET")
SOCIAL_AUTH_FACEBOOK_SCOPE = [
    'ads_management',
    'ads_read',
    'business_management',
    'email',
    'leads_retrieval',
    'manage_pages',
    'pages_manage_cta',
    'pages_manage_instant_articles',
    'pages_show_list',
    'public_profile',
    'publish_pages',
    'read_insights',
    'user_friends',
    'user_gender',
    'user_hometown',
    'user_likes',
    'user_link',
    'user_location',
    'user_photos',
    'user_posts',
    'user_tagged_places',
    'user_videos',
]
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'locale': 'ru_RU',
    'fields': 'id,name,picture'
}

LOGOUT_REDIRECT_URL = reverse_lazy('index')
