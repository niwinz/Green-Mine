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

from .generic import GenericView
from .decorators import login_required
from .. import models, forms


class AdminProjectsView(GenericView):
    def get(self, request, *args, **kwargs):
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
        
        projects = models.Project.objects.all()
        paginator = Paginator(projects, 20)
        page = paginator.page(page)

        context = {
            'is_paginated': True if paginator.count else False,
            'page': page,
            'csel': 'projects',
        }
        
        return self.render('config/projects.html', context)
    
    @login_required
    def dispatch(self, *args, **kwargs):
        return super(AdminProjectsView, self).dispatch(*args, **kwargs)


class ProfileView(GenericView):
    template_name = 'config/profile.html'

    def get(self, request):
        form = forms.ProfileForm(instance=request.user)
        context = {'form':form, 'csel':'profile'}
        return self.render(self.template_name, context)

    def post(self, request):
        form = forms.ProfileForm(request.POST, request.FILES, instance=request.user)
        context = {'form':form, 'csel':'profile'}

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

