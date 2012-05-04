# -*- coding: utf-8 -*-

from .common import *

from django.utils.translation import ugettext_lazy as _
import os.path, sys, os

ROOT_URLCONF = 'greenmine_mobile.urls'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '%(levelname)s:%(asctime)s:%(module)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'fileout': {
            'level':'DEBUG',
            'class':'logging.FileHandler',
            'filename': os.path.join(LOGS_PATH, 'greenmine_mobile.log'),
            'formatter': 'simple',
        },
        'queryhandler': {
            'level':'DEBUG',
            'class':'logging.FileHandler',
            'filename': os.path.join(LOGS_PATH, 'greenmine_mobile-querys.log'),
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers':['null'],
            'propagate': True,
            'level':'INFO',
        },
        'django.request': {
            'handlers': ['mail_admins', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends':{
            'handlers': ['queryhandler'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'main': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'asyncmail': {
            'handlers': ['console'],
            'level':'INFO',
            'propagate': False,
        }
    }
}
