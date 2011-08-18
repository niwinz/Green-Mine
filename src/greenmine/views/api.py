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
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, RedirectView, View

import logging, re
logger = logging.getLogger('greenmine')

from ..models import *
from ..forms import LoginForm
from ..utils import encrypt_password

from .decorators import login_required
from .generic import GenericView

class ApiLogin(GenericView):
    def post(self, request):
        login_form = LoginForm(request.POST, request = request)
        if not login_form.is_valid():
            return self.render_to_error(login_form.jquery_errors)

        request.session['current_user_id'] = login_form._user.id
        return self.render_to_ok({'userid': login_form._user.id, 'redirect_to': '/'})
