# -*- coding: utf-8 -*-

from django.conf import settings
from django.http import HttpResponseRedirect
from functools import wraps

def login_required(view_func):
    @wraps(view_func)
    def _wrapper(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return view_func(self, request, *args, **kwargs)
        else:
            return HttpResponseRedirect(settings.LOGIN_URL)

    return _wrapper

