from os import environ
from .base import *

# provide via Trais CI Dashboard
DAILYTRAN_BUILDER_API['amis'] = environ['AMIS_URL']
DAILYTRAN_BUILDER_API['apis'] = environ['APIS_URL']
DAILYTRAN_BUILDER_API['efish'] = environ['EFISH_URL']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'postgres',
        'PORT': '5432',
    },
}
