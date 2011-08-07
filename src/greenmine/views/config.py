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
from ..models import User
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
            
            messages.error(request, _(u'Integrity error: %(e)') % {'e':unicode(e)})
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
        form = ProjectForm(request.POST)
        context = {'form': form}
        
        if not form.is_valid():
            return self.render(self.template_name, context)

        sem = transaction.savepoint()
        try:
            project = form.save()
            #for post_key in request.POST.keys():
            #    user_rx_pos = self.user_rx.match(post_key)
            #    if not user_rx_pos:
            #        continue

            #    try:
            #        uproject = UserProject.objects.create(
            #        userobj = User.objects.get(pk=user_rx_pos.group('userid'))

                    


        except Exception as e:
            transaction.savepoint_rollback(sem)
            messages.error(request, _(u'Integrity error: %(e)') % {'e':unicode(e)})
            return self.render(self.template_name, {'form': form})
        
        transaction.savepoint_commit(sem)

        messages.info(request, _(u'Project %(pname) is successful saved.') % {'pname':project.name})
        return HttpResponseRedirect(reverse('web:projects'))

    @login_required
    def dispatch(self, *args, **kwargs):
        return super(ProjectCreateView, self).dispatch(*args, **kwargs)

