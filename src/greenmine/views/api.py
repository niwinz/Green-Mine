# -*- coding: utf-8 -*-

from django.views.decorators.cache import cache_page
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
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
from django.db.models import Q

import logging, re
logger = logging.getLogger('greenmine')

from greenmine.models import *
from greenmine import models, forms
from greenmine.utils import encrypt_password
from greenmine.views.decorators import login_required
from greenmine.views.generic import GenericView


class ApiLogin(GenericView):
    def post(self, request):
        login_form = forms.LoginForm(request.POST, request = request)
        if not login_form.is_valid():
            return self.render_to_error(login_form.jquery_errors)

        request.session['current_user_id'] = login_form._user.id
        return self.render_to_ok({'userid': login_form._user.id, 'redirect_to': '/'})


class UserListApiView(GenericView):
    def get(self, request):
        if "term" not in request.GET:
            return self.render_to_ok({'list':[]})
        
        term = request.GET['term']
        users = models.User.objects.filter(
            Q(username__istartswith=term) | Q(first_name__istartswith=term)
        )
        context = {'list': [{'id':x.id, 'label':x.first_name, 'value':x.first_name,
            'gravatar':'/static/auxiliar/imgs/gravatar.jpg'} for x in users]}
        return self.render_to_ok(context)


class TasksForMilestoneApiView(GenericView):
    def get(self, request, pslug, mid=None):
        project = get_object_or_404(models.Project, slug=pslug)
        
        issues = models.Issue.objects.none()
        if mid:
            try:
                milestone = project.milestones.get(pk=mid)
                issues = milestone.issues.all()
            except models.Milestone.DoesNotExist:
                return self.render_to_error("milestone does not exists")
        else:
            issues = project.issues.filter(milestone__isnull=True)

        response_list = []
        for issue in issues:
            response_dict = {
                'id': issue.id,
                'name': issue.subject,
                'to': issue.assigned_to and issue.assigned_to.first_name or None,
                'to_id': issue.assigned_to and issue.assigned_to.id or None,
                'state': issue.status,
                'state_view': issue.get_status_display(),
                'priority': issue.priority,
                'priority_view': issue.get_priority_display(),
                'type': issue.type,
                'type_view': issue.get_type_display(),
                'project_slug': issue.project.slug,
                'edit_url': issue.get_edit_api_url(),
            }
            response_list.append(response_dict)
        return self.render_to_ok({"tasks": response_list})


class ProjectDeleteApiView(GenericView):
    """ API Method for delete projects. """
    def post(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        project.delete()
        return self.render_to_ok()


class MilestoneCreateApiView(GenericView):
    def post(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        form = forms.MilestoneCreateForm(request.POST)
        if form.is_valid():
            milestone = models.Milestone.objects.create(
                name = form.cleaned_data['name'],
                project = project,
            )
            context = {
                'name':form.cleaned_data['name'],
                'id': milestone.id,
                'url': milestone.get_tasks_for_milestone_api_url(),
                'date': milestone.estimated_finish or '',
            }
            return self.render_to_ok(context)
        
        return self.render_to_error(form.jquery_errors)


class IssueCreateApiView(GenericView):
    def post(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        milestones = project.milestones.all()
        form = forms.IssueForm(milestone_queryset=milestones)
        if form.is_valid():
            issue = form.save()
            return self.render_to_ok()

        return self.render_to_error(form.jquery_errors)


class IssueEditApiView(GenericView):
    def post(self, request, pslug, issueid):
        issue = get_object_or_404(models.Issue, pk=issueid, project__slug=pslug)
        form = forms.IssueForm(request.POST, instance=issue)
        if form.is_valid():
            issue = form.save()
            return self.render_to_ok()

        return self.render_to_error(form.jquery_errors)


class I18NLangChangeApiView(GenericView):
    """ View for set language."""
    def get(self, request):
        if 'lang' in request.GET and request.GET['lang'] \
                                    in dict(settings.LANGUAGES).keys():
            request.session['django_language'] = request.GET['lang']
            if request.META.get('HTTP_REFERER', ''):
                return HttpResponseRedirect(request.META['HTTP_REFERER'])
            elif "next" in request.GET and request.GET['next']:
                return HttpResponseRedirect(request.GET['next'])
        
        return HttpResponseRedirect('/')


class ForgottenPasswordApiView(GenericView):
    def post(self, request):
        form = forms.ForgottenPasswordForm(request.POST)
        if form.is_valid():
            return self.render_to_ok({'redirect_to':'/'})

        return self.render_to_error(form.jquery_errors)
