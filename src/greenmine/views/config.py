# -*- coding: utf-8 -*-

from django.views.generic import View
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
from django.db import transaction

import re

from .generic import GenericView
from .decorators import login_required

from ..forms import ProfileForm, ProjectForm
from ..models import User, ROLE_CHOICES
from ..utils import encrypt_password

class ProfileView(GenericView):
    template_name = 'config/profile.html'

    def get(self, request):
        form = ProfileForm(instance=request.user)
        return self.render(self.template_name, {'form':form})

    def post(self, request):
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        context = {'form':form}

        if not form.is_valid():
            return self.render(self.template_name, context)

        sem = transaction.savepoint()
        try:
            request.user = form.save()
        except IntegrityError as e:
            transaction.savepoint_rollback(sem)
            
            messages.error(request, _(u'Integrity error: %(e)s') % {'e':unicode(e)})
            return self.render(self.template_name, context)
        
        transaction.savepoint_commit(sem)

        messages.info(request, _(u'Profile save success!'))
        return HttpResponseRedirect(reverse('web:profile'))

    @login_required
    def dispatch(self, *args, **kwargs):
        return super(ProfileView, self).dispatch(*args, **kwargs)


class ProjectCreateView(GenericView):
    template_name = 'config/project.html'
    user_rx = re.compile(r'^user_(?P<userid>\d+)$', flags=re.U)

    def get(self, request):
        form = ProjectForm()
        return self.render(self.template_name, {'form':form})

    def post(self, request):
        form = ProjectForm(request.POST, request=request)
        context = {'form': form}
        
        if not form.is_valid():
            return self.render(self.template_name, context)

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
                messages.error(request, emsg)
                return self.render(self.template_name, context)

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

    @login_required
    def dispatch(self, *args, **kwargs):
        return super(ProjectCreateView, self).dispatch(*args, **kwargs)

