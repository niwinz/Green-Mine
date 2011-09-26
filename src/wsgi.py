# -*- coding: utf-8 -*-

import os
import os.path
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings.local'

current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'extern'))
sys.path.insert(0, os.path.join(current_dir, 'extern', 'django-randomfilenamestorage'))
sys.path.insert(0, os.path.join(current_dir, 'extern', 'django-html5-forms'))

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
