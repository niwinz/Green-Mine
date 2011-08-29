# -*- coding: utf-8 -*-

from django.views.generic import View
from django.views.decorators.cache import cache_page
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode
from django.http import HttpResponseRedirect, HttpResponse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.core.mail import EmailMessage
from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.template import RequestContext, loader
from django.contrib import messages
from django.db.utils import IntegrityError
from django.db import transaction
from django.utils.decorators import method_decorator
from django.utils import simplejson

from .generic import GenericView, ProjectGenericView
from .decorators import login_required
from .. import models, forms

import re


class LoginView(GenericView):
    def get(self, request, *args, **kwargs):
        login_form, forgotten_password_form = forms.LoginForm(request=request), forms.ForgottenPasswordForm()
        return self.render('login.html', 
            {'form': login_form, 'form2': forgotten_password_form})


class ProjectsView(GenericView):
    def get(self, request, *args, **kwargs):
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
        
        projects = request.user.projects.all()
        paginator = Paginator(projects, 20)
        page = paginator.page(page)

        context = {
            'is_paginated': True if paginator.count else False,
            'page': page,
        }
        
        return self.render('projects.html', context)
    
    @login_required
    def dispatch(self, *args, **kwargs):
        return super(ProjectsView, self).dispatch(*args, **kwargs)


class ProjectView(GenericView):
    @login_required
    def get(self, request, slug):
        project = get_object_or_404(models.Project, slug=slug)
        context = {
            'filtersform': forms.FiltersForm(queryset=project.participants.all()),
            'project': project
        }
        return self.render('dashboard.html', context)


class ProjectCreateView(GenericView):
    template_name = 'config/project.html'
    user_rx = re.compile(r'^user_(?P<userid>\d+)$', flags=re.U)

    def parse_roles(self):
        user_role = {}

        for post_key in self.request.POST.keys():
            user_rx_pos = self.user_rx.match(post_key)
            if not user_rx_pos:
                continue

            user_role[user_rx_pos.group('userid')] = self.request.POST[post_key]

        role_values = dict(models.ROLE_CHOICES).keys()
        invalid_role = False
        for role in user_role.values():
            if role not in role_values:
                invalid_role = True
                break
            
        return {} if invalid_role else user_role

    def get(self, request):
        form = forms.ProjectForm()
        context = {'form':form, 'roles': models.ROLE_CHOICES}
        return self.render(self.template_name, context)

    def post(self, request):
        form = forms.ProjectForm(request.POST, request=request)
        context = {'form': form, 'roles': models.ROLE_CHOICES}
        
        if not form.is_valid():
            return self.render(self.template_name, context)
        
        sem = transaction.savepoint()
        try:
            user_role = self.parse_roles()
            if not user_role:
                transaction.savepoint_rollback(sem)
                emsg = _(u'Debe especificar al menos una persona al proyecto')
                messages.error(request, emsg)
                return self.render(self.template_name, context)
            
            project = form.save()
            for userid, role in user_role.iteritems():
                models.ProjectUserRole.objects.create(
                    project = project,
                    user = models.User.objects.get(pk=userid),
                    role = role
                )

        except Exception as e:
            transaction.savepoint_rollback(sem)
            messages.error(request, _(u'Integrity error: %(e)s') % {'e':unicode(e)})
            return self.render(self.template_name, {'form': form})
        
        transaction.savepoint_commit(sem)
        messages.info(request, _(u'Project %(pname)s is successful saved.') % {'pname':project.name})
        return HttpResponseRedirect(reverse('web:projects'))

    @login_required
    def dispatch(self, *args, **kwargs):
        return super(ProjectCreateView, self).dispatch(*args, **kwargs)


class ProjectEditView(ProjectCreateView):
    template_name = 'config/project-edit.html'
    user_rx = re.compile(r'^user_(?P<userid>\d+)$', flags=re.U)

    def get(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        form = forms.ProjectForm(instance=project)
        context = {'form':form, 'roles': ROLE_CHOICES}
        return self.render(self.template_name, context)

    def post(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        form = forms.ProjectForm(request.POST, request=request, instance=project)
        context = {'form': form, 'roles': ROLE_CHOICES}
        
        if not form.is_valid():
            return self.render(self.template_name, context)
        
        sem = transaction.savepoint()
        try:
            user_role = self.parse_roles()
            if not user_role:
                transaction.savepoint_rollback(sem)
                emsg = _(u'Debe especificar al menos una persona al proyecto')
                messages.error(request, emsg)
                return self.render(self.template_name, context)

            project = form.save()
            models.ProjectUserRole.objects.find(project=project).delete()
            for userid, role in user_role.iteritems():
                models.ProjectUserRole.objects.create(
                    project = project,
                    user = User.objects.get(pk=userid),
                    role = role
                )

        except Exception as e:
            transaction.savepoint_rollback(sem)
            messages.error(request, _(u'Integrity error: %(e)s') % {'e':unicode(e)})
            return self.render(self.template_name, {'form': form})
        
        transaction.savepoint_commit(sem)
        messages.info(request, _(u'Project %(pname)s is successful saved.') % {'pname':project.name})
        return HttpResponseRedirect(reverse('web:projects'))
