# -*- coding: utf-8 -*-

from .common_mobile import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
USE_ETAGS=False

TEMPLATE_CONTEXT_PROCESSORS += [
    "django.core.context_processors.debug",
]

#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

