# -*- coding: utf-8 -*-

from .common import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
USE_ETAGS=False

TEMPLATE_CONTEXT_PROCESSORS += [
    "django.core.context_processors.debug",
]

INSTALLED_APPS += [
    'django_dbstorage',
]

MEDIA_ROOT = None
#MEDIA_URL  = None

DEFAULT_FILE_STORAGE = 'greenmine.storage.RandomFilenameDBStorage'
#DEFAULT_FILE_STORAGE = 'django_dbstorage.storage.DatabaseStorage'
