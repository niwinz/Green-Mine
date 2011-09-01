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

class LoginView(views.LoginView):
    template_name = 'mobile/login.html'

    def post(self, request):
        form = forms.LoginForm(request.POST, request = request)
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

class ProjectIssuesView(GenericView):
    def get(self, request, pslug, mid):
        project = get_object_or_404(models.Project, slug=pslug)
        mid = int(mid)       

        if mid == 0:
            issues = project.issues.filter(milestone__isnull=True)
            mon_issues = []
        else:
            milestone = get_object_or_404(project.milestones, pk=mid)
            mon_issues = milestone.issues.filter(assigned_to=request.user)
            issues = milestone.issues.exclude(assigned_to=request.user)

        context = {'issues': issues, 'mon_issues': mon_issues}
        return self.render('mobile/includes/dashboard_issues.html', context)

class IssueView(views.IssueView):
    template_name = 'mobile/issue.html'

