# -*- coding: utf-8 -*-

from django.views.decorators.cache import cache_page
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode
from django.http import HttpResponseRedirect, HttpResponse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.core.mail import EmailMessage
from django.utils import simplejson
from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.template import RequestContext, loader
from django.contrib import messages
from django.db.utils import IntegrityError
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, RedirectView, View

import logging
logger = logging.getLogger('greenmine')


from greenmine.models import *
from greenmine.utils import *

class ApiView(View):
    def render_to_response(self, context):
        if isinstance(context, dict):
            response_data = simplejson.dumps(context, cls=LazyEncoder, indent=4, sort_keys=True)
        else:
            response_data = context
        return HttpResponse(response_data, mimetype='text/plain')

    def render_to_error(self, context):
        response_dict = {'valid': False, 'errors':[]}
        if isinstance(context, (str, unicode, dict)):
            response_dict['errors'].append(context)
        elif isinstance(context, (list,tuple)):
            response_dict['errors'] = context

        return self.render_to_response(response_dict)

    def render_to_ok(self, context):
        response = {'valid': True, 'errors': []}
        response.update(context)
        return self.render_to_response(response)


class RestrictedApiView(ApiView):
    @method_decorator(api_login_required)
    def dispatch(self, *args, **kwargs):
        return super(RestrictedApiView, self).dispatch(*args, **kwargs)


from greenmine.forms import LoginForm

class ApiLogin(ApiView):
    def post(self, request):
        login_form = LoginForm(request.POST)
        if not login_form.is_valid():
            return self.render_to_error(login_form.jquery_errors)

        request.session['current_user_id'] = login_form._user.id
        return self.render_to_ok({'userid': login_form._user.id,
            'redirect_to': '/'})

