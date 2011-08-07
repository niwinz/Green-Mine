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
from ..forms import *
from ..utils import encrypt_password

from .decorators import login_required

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
        return self.render_to_ok({'userid': login_form._user.id, 'redirect_to': '/'})


class ApiProjectCreateView(RestrictedApiView):
    user_rx = re.compile(r'^user_(?P<userid>\d+)$', flags=re.U)

    def post(self, request):
        form = ProjectForm(request.POST, request=request)
        context = {'form': form}
        
        if not form.is_valid():
            return self.render_to_error(form.jquery_errors)

        sem = transaction.savepoint()
        try:
            user_role = {}

            for post_key in request.POST.keys():
                user_rx_pos = self.user_rx.match(post_key)
                if not user_rx_pos:
                    continue

                user_role[user_rx_pos.group('userid')] = request.POST[post_key]
            
            if not user_role:
                transaction.savepoint_rollback(sem)
                emsg = _(u'Debe especificar al menos una persona al proyecto')
                return self.render_to_error([emsg])

            #: test user roles
            role_values = dict(ROLE_CHOICES).keys()
            invalid_role = False
            for role in user_role.values():
                if role not in role_values:
                    invalid_role = True
                    break

            if invalid_role:
                emsg = _(u'Uno o mas roles son invalidos.')
                messages.error(request, emsg)
                return self.render(self.template_name, context)

            project = form.save()

        except Exception as e:
            transaction.savepoint_rollback(sem)
            messages.error(request, _(u'Integrity error: %(e)s') % {'e':unicode(e)})
            return self.render(self.template_name, {'form': form})
        
        transaction.savepoint_commit(sem)

        messages.info(request, _(u'Project %(pname) is successful saved.') % {'pname':project.name})
        return HttpResponseRedirect(reverse('web:projects'))
