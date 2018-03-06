from aosd.settings.base import *


DEBUG = True


DATABASES['subscriptions'] = {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'aosd_subscriptions',
    'USER': 'postgres',
    'PASSWORD': '',
    'HOST': 'localhost',
    'PORT': 5432
}


EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_FROM_EMAIL = ''
EMAIL_USE_TLS = True
