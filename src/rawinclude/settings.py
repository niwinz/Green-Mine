# -*- coding: utf-8 -*-

from django.conf import settings

RAWINCLUDE_CACHE = getattr(settings, 'RAWINCLUDE_CACHE', True)
