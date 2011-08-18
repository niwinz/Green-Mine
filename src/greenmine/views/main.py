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

from .generic import GenericView, ProjectGenericView
from .decorators import login_required
from ..forms import LoginForm, ForgottenPasswordForm
from ..models import Project


class LoginView(GenericView):
    def get(self, request, *args, **kwargs):
        login_form, forgotten_password_form = LoginForm(), ForgottenPasswordForm()
        return self.render('login.html', 
            {'form': login_form, 'form2': forgotten_password_form})


class ProjectsView(GenericView):
    def get(self, request, *args, **kwargs):
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
        
        if request.user.is_superuser:
            projects = Project.objects.all()
        else:
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


class ProjectView(ProjectGenericView):
    def get(self, request, *args, **kwargs):
        context = self.get_context()
        return self.render('dashboard.html', context)

    @login_required
    def dispatch(self, *args, **kwargs):
        return super(ProjectView, self).dispatch(*args, **kwargs)


