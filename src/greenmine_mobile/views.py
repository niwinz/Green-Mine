# -*- coding: utf-8 -*-

from django.views.generic import View
from django.views.decorators.cache import cache_page
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.template import RequestContext, loader
from django.contrib import messages

from django.db.utils import IntegrityError
from django.db import transaction
from django.utils.decorators import method_decorator
from django.utils import simplejson

from greenmine.views.generic import GenericView, ProjectGenericView
from greenmine.views.decorators import login_required
from greenmine import models, forms
from greenmine.views import main as views
from greenmine_mobile import forms as mforms

class LoginView(GenericView):
    template_name = 'mobile/login.html'

    def get(self, request, *args, **kwargs):
        form = mforms.LoginForm(request=request)
        return self.render(self.template_name,
            {'form': form})

    def post(self, request):
        form = mforms.LoginForm(request.POST, request = request)
        if not form.is_valid():
            return self.render(self.template_name, {'form':form})

        user_profile = form._user.get_profile()
        if user_profile.default_language:
            request.session['django_language'] = user_profile.default_language

        return HttpResponseRedirect('/')


class ProjectsView(views.ProjectsView):
    template_name = 'mobile/projects.html'


class ProjectView(views.ProjectView):
    template_name = 'mobile/dashboard.html'


class ProjectUssView(GenericView):
    def get(self, request, pslug, mid):
        project = get_object_or_404(models.Project, slug=pslug)
        mid = int(mid)       

        if mid == 0:
            uss = project.uss.filter(milestone__isnull=True)
        else:
            milestone = get_object_or_404(project.milestones, pk=mid)
            uss = milestone.uss.all()

        uss = uss.order_by('-priority')

        context = {'uss': uss}
        return self.render('mobile/includes/dashboard_uss.html', context)


class UsView(views.UsView):
    template_name = 'mobile/us.html'


class UsCreate(GenericView):
    template_name = 'mobile/us-create.html'

    @login_required
    def get(self, request, pslug, mid):
        project = get_object_or_404(models.Project, slug=pslug)
        form = mforms.UsCreateForm()
        context = {'form':form}
        return self.render(self.template_name, context)


class ProfileView(GenericView):
    template_name = 'mobile/profile.html'

    @login_required
    def get(self, request, username=None):
        if username:
            user = get_object_or_404(models.User,username=username)
        else:
            user = request.user

        context = {'userobj': user}
        return self.render(self.template_name, context)
