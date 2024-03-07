import os
import environ
from django.utils.translation import ugettext_lazy as _

BASE_DIR = environ.Path(__file__) - 2

# Load operating system environment variables and then prepare to use them
env = environ.Env()

# Read a optional env file if not configure from environment variables
if os.path.exists(BASE_DIR('.env')):
    environ.Env.read_env(BASE_DIR('.env'))

SECRET_KEY = env.str('SECRET_KEY')

DEBUG = env.bool('DEBUG')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',

    # Third-part packages
    'rest_framework',
    'crispy_forms',
    'markdown_deux',
    'widget_tweaks',
    'django_celery_beat',
    'django_celery_results',
    'rangefilter',
    'tracking',
    'ckeditor',
    'tagulous',
    'django_db_logger',

    # Local apps
    'dashboard',
    'apps.accounts',
    'apps.configs',
    'apps.crops',
    'apps.rices',
    'apps.fruits',
    'apps.flowers',
    'apps.hogs',
    'apps.rams',
    'apps.chickens',
    'apps.ducks',
    'apps.gooses',
    'apps.seafoods',
    'apps.cattles',
    'apps.dailytrans',
    'apps.watchlists',
    'apps.posts',
    'apps.comments',
    'apps.events',
    'apps.logs',
    'apps.feed',
    'apps.naifchickens',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'tracking.middleware.VisitorTrackingMiddleware',
]

ROOT_URLCONF = 'dashboard.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(BASE_DIR('templates'))],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.contrib.messages.context_processors.messages',
                # custom contexts
                'dashboard.context_processors.ga_tracking_id',
                'dashboard.context_processors.use_ga',
                'dashboard.context_processors.aprp_version'
            ],
        },
    },
]

WSGI_APPLICATION = 'dashboard.wsgi.application'


# Logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
    },
    'handlers': {
        'db_log': {
            'level': 'DEBUG',
            'class': 'django_db_logger.db_log_handler.DatabaseLogHandler'
        },
        'aprp_log': {
            'level': 'DEBUG',
            'class': 'apps.logs.db_log_handler.DatabaseLogHandler'
        },
    },
    'loggers': {
        'db': {
            'handlers': ['db_log'],
            'level': 'DEBUG'
        },
        'aprp': {
            'handlers': ['aprp_log'],
            'level': 'DEBUG'
        }
    }
}


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env.str('POSTGRES_DB'),
        'USER': env.str('POSTGRES_USER'),
        'PASSWORD': env.str('POSTGRES_PASSWORD'),
        'HOST': env.str('POSTGRES_HOST'),
        'PORT': 5432,
    },
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'zh-hant'

# Local time zone for this installation. All choices can be found here:
# https://en.wikipedia.org/wiki/List_of_tz_zones_by_name (although not all
# systems may support all possibilities). When USE_TZ is True, this is
# interpreted as the default user time zone.
TIME_ZONE = 'Asia/Taipei'

# If you set this to True, Django will use timezone-aware datetimes
# .
USE_TZ = True

# Languages we provide translations for, out of the box.
LANGUAGES = [
    ('zh-hant', _('Traditional Chinese')),
    ('en', _('English')),
]

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
LOCALE_PATHS = [
    str(BASE_DIR('locale')),
]


# Settings for language cookie
LANGUAGE_COOKIE_NAME = 'django_language'
LANGUAGE_COOKIE_AGE = None
LANGUAGE_COOKIE_DOMAIN = None
LANGUAGE_COOKIE_PATH = '/'


# If you set this to True, Django will format dates, numbers and calendars
# according to user current locale.
USE_L10N = False


# Static files (CSS, JavaScript, Images)
STATICFILES_DIRS = [
    str(BASE_DIR('static'))
]
STATIC_URL = '/static/'

# WhiteNoise

STATIC_ROOT = str(BASE_DIR("live-static-files", "static-root"))
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'
MEDIA_URL = "/media/"
MEDIA_ROOT = str(BASE_DIR("live-static-files", "media-root"))

SERVE_MEDIA_FILES = False  # make whitenoise serving media files

# All-auth

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
)
SITE_ID = 1
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/login/'

# Crispy

CRISPY_TEMPLATE_PACK = 'bootstrap3'

# Fixtures

FIXTURE_DIRS = [
    str(BASE_DIR('fixtures')),
    str(BASE_DIR('fixtures/rices')),
    str(BASE_DIR('fixtures/crops')),
    str(BASE_DIR('fixtures/crops/origin')),
    str(BASE_DIR('fixtures/crops/wholesale')),
    str(BASE_DIR('fixtures/fruits')),
    str(BASE_DIR('fixtures/fruits/origin')),
    str(BASE_DIR('fixtures/fruits/wholesale')),
    str(BASE_DIR('fixtures/flowers/wholesale')),
    str(BASE_DIR('fixtures/hogs')),
    str(BASE_DIR('fixtures/rams')),
    str(BASE_DIR('fixtures/chickens')),
    str(BASE_DIR('fixtures/ducks')),
    str(BASE_DIR('fixtures/gooses')),
    str(BASE_DIR('fixtures/seafoods/origin')),
    str(BASE_DIR('fixtures/seafoods/wholesale')),
    str(BASE_DIR('fixtures/cattles')),
    str(BASE_DIR('fixtures/watchlists')),
    str(BASE_DIR('fixtures/events')),
    str(BASE_DIR('fixtures/festivals')),
    str(BASE_DIR('fixtures/feed')),
    str(BASE_DIR('fixtures/naifchickens')),
    str(BASE_DIR('fixtures/last5years')),
]

# Rest-framework

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    "DATE_INPUT_FORMATS": ["%Y/%m/%d"],
}


# Redis

REDIS_URL = 'redis://{host}:{port}'.format(host=env.str('REDIS_HOST'), port=6379)


# Celery

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

CELERY_IMPORTS = (
    'dashboard.tasks',
    'apps.rices.tasks',
    'apps.crops.tasks',
    'apps.fruits.tasks',
    'apps.hogs.tasks',
    'apps.rams.tasks',
    'apps.chickens.tasks',
    'apps.ducks.tasks',
    'apps.gooses.tasks',
    'apps.seafoods.tasks',
    'apps.cattles.tasks',
    'apps.watchlists.tasks',
    'apps.dailytrans.tasks',
    'apps.feed.tasks',
    'apps.naifchickens.tasks',
)

# Session Settings
SESSION_COOKIE_AGE = 60 * 60 * 2
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_HTTPONLY = True   #   disable for csrf token post 403 error
CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SAMESITE = 'None'  # django 1.9 not support
# CSRF_COOKIE_SAMESITE = 'None'     # django 1.9 not support

# Django Security Settings
SECURE_HSTS_SECONDS = 15768000   # Strict-Transport-Security, 6 months
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_REFERRER_POLICY = 'same-origin'  # Referrer-Policy; django 1.9 not support
SECURE_CONTENT_TYPE_NOSNIFF = True  # X-Content-Type-Options
SECURE_BROWSER_XSS_FILTER = True    # X-XSS-Protection

# Google Analytics
USE_GA = env.bool('USE_GA', default=False)
GA_TRACKING_ID = env.str('GA_TRACKING_ID', default='')

# Email Backend
EMAIL_BACKEND = env.str('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = env.str('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)

EMAIL_HOST_USER = env.str('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env.str('DEFAULT_FROM_EMAIL', default='')
ADMINS = [(user, user) for user in env.list('ADMINS', default=[])]

# Password limits
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
]

# Aprp Release Version
APRP_VERSION = '19.11.0'

# API urls
DAILYTRAN_BUILDER_API = {
    'cattle': 'https://data.coa.gov.tw/Service/OpenData/BeefPriceService.aspx?',
    'eir019': 'https://data.coa.gov.tw/Service/OpenData/FromM/AnimalTransData.aspx?',
    'eir030': 'https://data.coa.gov.tw/Service/OpenData/FromM/FarmTransData.aspx?',
    'eir032': 'https://data.coa.gov.tw/Service/OpenData/FromM/AquaticTransData.aspx?',
    'eir49': 'https://data.coa.gov.tw/Service/OpenData/FromM/PoultryTransBoiledChickenData.aspx?',
    'eir049': 'https://data.coa.gov.tw/Service/OpenData/FromM/PoultryTransLocalRedChickenData.aspx?',
    'eir50': 'https://data.coa.gov.tw/Service/OpenData/FromM/PoultryTransGooseDailyPriceData.aspx?',
    'eir050': 'https://data.coa.gov.tw/Service/OpenData/FromM/PoultryTransLocalBlackChickenData.aspx?',
    'eir51': 'https://data.coa.gov.tw/Service/OpenData/FromM/PoultryTransGooseDuckData.aspx?',
    'eir097': 'https://data.coa.gov.tw/Service/OpenData/FromM/RicepriceData.aspx?',
    'eir107': 'https://data.coa.gov.tw/Service/OpenData/FromM/SheepTransData.aspx?',
    'rice_avg': 'https://data.coa.gov.tw/Service/OpenData/Ricepriceavg.aspx?',
    'amis': env.str('BUILDER_API_AMIS_URL', default=''),
    'apis': env.str('BUILDER_API_APIS_URL', default=''),
    'efish': env.str('BUILDER_API_EFISH_URL', default=''),
    'feed': 'https://www.naif.org.tw/memberLogin.aspx?frontTitleMenuID=105',   #飼料和環南市場雞隻等數據是從中央畜產會登入帳號爬蟲取得
    'naifchickens': 'https://www.naif.org.tw/memberLogin.aspx?frontTitleMenuID=105',   #飼料和環南市場雞隻等數據是從中央畜產會登入帳號爬蟲取得
}

# Hide login
DJANGO_ADMIN_PATH = env.str('DJANGO_ADMIN_PATH', default='admin')

# Google Drive

GOOGLE_DRIVE_CLIENT_ID = env.str('GOOGLE_DRIVE_CLIENT_ID')
GOOGLE_DRIVE_CLIENT_SECRET = env.str('GOOGLE_DRIVE_CLIENT_SECRET')
GOOGLE_DRIVE_REFRESH_TOKEN = env.str('GOOGLE_DRIVE_REFRESH_TOKEN')

DAILY_REPORT_FOLDER_ID = env.str('DAILY_REPORT_FOLDER_ID', default='')
TEST_DAILY_REPORT_FOLDER_ID = env.str('TEST_DAILY_REPORT_FOLDER_ID', default='')
FESTIVAL_REPORT_FOLDER_ID = env.str('FESTIVAL_REPORT_FOLDER_ID', default='')

# Naif login
NAIF_ACCOUNT = env.str('NAIF_ACCOUNT')
NAIF_PASSWORD = env.str('NAIF_PASSWORD')
PYTESSERACT_PATH = env.str('PYTESSERACT_PATH')
USER_AGENT = env.str('User_Agent')
