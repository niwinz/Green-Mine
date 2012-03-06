# -*- coding: utf-8 -*- 

from django.conf import settings
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import Promise
from django.utils.encoding import force_unicode

import datetime, hashlib, os.path, os
import random, string
import unicodedata


class Singleton(type):
    """ Singleton metaclass. """
    def __init__(cls, name, bases, dct):
        cls.__instance = None
        type.__init__(cls, name, bases, dct)
 
    def __call__(cls, *args, **kw):
        if cls.__instance is None:
            cls.__instance = type.__call__(cls, *args,**kw)
        return cls.__instance


def clear_model_dict(data):
    hidden_fields = ['password']

    new_dict = {}
    for key, val in data.items():
        if not key.startswith('_') and key not in hidden_fields:
            new_dict[key] = val

    return new_dict


def normalize_tagname(tagname):
    value = unicodedata.normalize('NFKD', tagname).encode('ascii', 'ignore')
    return value.lower()
