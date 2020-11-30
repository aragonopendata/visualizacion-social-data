from aosd.settings.base import *


DEBUG = True 


ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    '193.146.116.193',
    '172.27.38.119',
    'miv-aodfront-01.aragon.local'
]

ADMINS = (
    ('', '@.es'),
)


DATABASES['subscriptions'] = {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'aosd',
    'USER': 'aosd_user',
    'PASSWORD': '',
    'HOST': '',
    'PORT': 5432
}


EMAIL_HOST = '188.244.81.8' # 'smtp.aragon.es'
EMAIL_PORT = 587
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_FROM_EMAIL = ''
EMAIL_USE_TLS = True


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/escucha/webapi.log',
            'maxBytes': 1024*1024*500, # 500 MB
            'backupCount': 50, # 50 files
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'main': { # App name
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    }
}
