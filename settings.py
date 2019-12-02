import os
from pathlib import Path

from dotenv import load_dotenv

try:
    env_path = Path('.', 'env.config').resolve()
except:
    raise Exception("[BGM] Please provide a valid .env file")

# Read keys from dotenv file
load_dotenv(dotenv_path=env_path, verbose=True)
SECRET_KEY = os.getenv('SECRET_KEY')
SOCIAL_AUTH_FACEBOOK_KEY = os.getenv("SOCIAL_AUTH_FACEBOOK_KEY")
SOCIAL_AUTH_FACEBOOK_SECRET = os.getenv("SOCIAL_AUTH_FACEBOOK_SECRET")
GOOGLE_MAPS_KEY = os.getenv("GOOGLE_MAPS_KEY")

CORE_APP_NAME='lodreranker'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1'
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social_django',
    'sslserver',
    'crispy_forms',
    f'{CORE_APP_NAME}',
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

CRISPY_TEMPLATE_PACK = 'bootstrap4'

ROOT_URLCONF = 'urls'
WSGI_APPLICATION = 'wsgi.application'
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

AUTH_USER_MODEL = f'{CORE_APP_NAME}.CustomUser'

AUTH_PASSWORD_VALIDATORS = [
    # NOT NEEDED ATM
    # {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    # {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    # {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    # {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

AUTHENTICATION_BACKENDS = [
    'social_core.backends.facebook.FacebookOAuth2',
    'django.contrib.auth.backends.ModelBackend',
    f'{CORE_APP_NAME}.custom_auth.HashedPasswordAuthBackend',
]

SOCIAL_AUTH_FACEBOOK_SCOPE = [
    'email',
    'public_profile',
    'user_friends','user_gender', 'user_hometown', 'user_likes', 'user_link', 'user_location', 'user_photos', 'user_posts', 'user_tagged_places', 'user_videos',
]

SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'locale': 'it_IT',
    #'fields': 'id, name, email, picture.type(large), link'
    # UNCOMMENT WHEN NEEDED
    # 'fields': 'id, name, email, picture.type(large), link, feed, posts, likes, albums, movies, books, music'
    'fields': 'id, name, email, picture.type(large), link, movies, books, music'
}

SOCIAL_AUTH_FACEBOOK_EXTRA_DATA = [
    ('name', 'name'),
    ('email', 'email'),
    ('picture', 'picture'),
    ('link', 'profile_url'),
    # UNCOMMENT WHEN NEEDED
    # ('feed', 'feed'),
    # ('posts', 'posts'),
    # ('albums', 'albums'),
    # ('likes', 'likes'),
    ('movies', 'movies'),
    ('books', 'books'),
    ('music', 'artists'),
]

LOGIN_URL = '/users/login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

SOCIAL_AUTH_FACEBOOK_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    f'{CORE_APP_NAME}.custom_auth.is_skip',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
    # 'social_core.pipeline.debug.debug',
    f'{CORE_APP_NAME}.custom_auth.redirect_registration',

)

SOCIAL_AUTH_FIELDS_STORED_IN_SESSION = [
    'skip_creation'
]
