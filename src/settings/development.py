# -*- coding: utf-8 -*-

from .common import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
USE_ETAGS = False

TEMPLATE_CONTEXT_PROCESSORS += [
    "django.core.context_processors.debug",
]
