from os import environ
from .base import *

# provide via Trais CI Dashboard
SECRET_KEY = environ['SECRET_KEY']
DAILYTRAN_BUILDER_API['amis'] = environ['AMIS_URL']
DAILYTRAN_BUILDER_API['apis'] = environ['APIS_URL']
DAILYTRAN_BUILDER_API['efish'] = environ['EFISH_URL']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'travis_ci_test',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '',
    }
}