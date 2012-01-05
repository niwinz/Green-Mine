# -*- coding: utf-8 -*-

from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson
from functools import wraps

from ..utils import LazyEncoder

def login_required(view_func):
    @wraps(view_func)
    def _wrapper(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return view_func(self, request, *args, **kwargs)
        else:
            if request.is_ajax():
                response_dict = {'valid': False, 'errors':[_(u"Permission denied.")]}
                response_data = simplejson.dumps(response_dict, cls=LazyEncoder, indent=4, sort_keys=True)
                return HttpResponse(response_data, mimetype='text/plain')
            else:
                return HttpResponseRedirect(settings.LOGIN_URL)

    return _wrapper

