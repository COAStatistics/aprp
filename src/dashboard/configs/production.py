from .base import *

# Celery

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
CSRF_COOKIE_SECURE = True

# Django Security Settings
SECURE_HSTS_SECONDS = 15768000   # Strict-Transport-Security, 6 months
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True  # X-Content-Type-Options
SECURE_BROWSER_XSS_FILTER = True    # X-XSS-Protection

# Google Analytics
USE_GA = env.bool('USE_GA', default=False)
GA_TRACKING_ID = env.str('GA_TRACKING_ID', default='')


# Aprp Release Version
APRP_VERSION = '19.11.0'

# Hide login
DJANGO_ADMIN_PATH = env.str('DJANGO_ADMIN_PATH', default='admin')
