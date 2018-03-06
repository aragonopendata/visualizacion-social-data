import os
import socket

# SET THE ENVIRONMENT

_HOSTNAME = socket.gethostname()

_PRODUCTION_SERVERS = (
	'aosd-1',
)

_STAGING_SERVERS = (
)

_CUSTOM_MACHINES = (
)

PRODUCTION_ENVIRONMENT = 0
STAGING_ENVIRONMENT = 1
DEVELOPMENT_ENVIRONMENT = 2
CUSTOM_ENVIRONMENT = 3

if _HOSTNAME in _PRODUCTION_SERVERS:
	# Production environment
	ENVIRONMENT = PRODUCTION_ENVIRONMENT
elif _HOSTNAME in _STAGING_SERVERS:
	# Staging environment
	ENVIRONMENT = STAGING_ENVIRONMENT
elif _HOSTNAME in _CUSTOM_MACHINES:
	# Custom environment
	ENVIRONMENT = CUSTOM_ENVIRONMENT
else:
	# Development environment
	ENVIRONMENT = DEVELOPMENT_ENVIRONMENT


if ENVIRONMENT == PRODUCTION_ENVIRONMENT:
	# Production environment
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aosd.settings.production")
elif ENVIRONMENT == CUSTOM_ENVIRONMENT:
	# Custom environment
	settings_file = _HOSTNAME.replace('.', '_')
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aosd.settings." + settings_file)
else:
	# Development environment
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aosd.settings.development")
