# -*- coding: utf-8 -*- 

from django.conf import settings
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import Promise
from django.utils.encoding import force_unicode
from django.utils import simplejson

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


def encrypt_password(password):
    """ Make password hash. """
    return hashlib.sha256(password).hexdigest()


def make_repo_location(project):
    project_repo_path = os.path.join(settings.REPO_ROOT, project.slug)
    if not os.path.exists(project_repo_path):
        os.mkdir(project_repo_path)

    return project_repo_path, project.slug


def clear_model_dict(data):
    hidden_fields = ['password']

    new_dict = {}
    for key, val in data.items():
        if not key.startswith('_') and key not in hidden_fields:
            new_dict[key] = val

    return new_dict


class LazyEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_unicode(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%S')
        return super(LazyEncoder, self).default(obj)


def random_name(chars=string.ascii_lowercase, length=16, prefix='',suffix=''):
    if length - len(prefix)-len(suffix) < 0:
        raise ValueError("length - len(prefix)-len(suffix) is < 0")

    filename = ''.join([random.choice(chars) for i in range(length-len(prefix)-len(suffix))])
    filename = prefix + filename + suffix
    return filename


def api_login_required(function):
    def _view_wrapper(request, *args, **kwargs):
        response = {'id': None, 'valid': False, 'errors':[_(u'You have to start session to proceed')]}
        if request.user.is_authenticated() or request.path == '/api/login':
            return function(request, *args, **kwargs)
        else:
            response_data = simplejson.dumps(response, cls=LazyEncoder, indent=4, sort_keys=True)
            return HttpResponse(response_data, mimetype='text/plain')

    return _view_wrapper


def normalize_tagname(tagname):
    value = unicodedata.normalize('NFKD', tagname).encode('ascii', 'ignore')
    return value.lower()
