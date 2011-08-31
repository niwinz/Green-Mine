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

        user_profile = login_form._user.get_profile()
        if user_profile.default_language:
            request.session['django_language'] = user_profile.default_language

        return self.render_to_ok({'userid': login_form._user.id, 'redirect_to': '/'})


class UserListApiView(GenericView):
    @login_required
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


class MilestonesForProjectApiView(GenericView):
    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        
        milestones = []
        for ml in project.milestones.all():
            total_tasks = ml.issues.count()
            total_tasks_completed = ml.issues.filter(status__in=['fixed','invalid']).count()
            milestones.append({
                'id': ml.id,
                'url': ml.get_tasks_for_milestone_api_url(),
                'edit_url': ml.get_edit_api_url(),
                'name': ml.name,
                'estimated_finish': ml.estimated_finish and \
                    ml.estimated_finish.strftime('%d/%m/%Y') or '',
                'completed_tasks': total_tasks_completed,
                'total_tasks': total_tasks,
            })

        total_unassigned_tasks = project.issues.filter(milestone__isnull=True).count()
        total_unassigned_completed_tasks = project.issues.filter(
            milestone__isnull=True, 
            status__in=['fixed','invalid']
        ).count()

        milestones.append({
            'id': 0,
            'url': ml.project.get_unasigned_tasks_api_url(),
            'edit_url': '',
            'name': _('Unasigned'),
            'estimated_finish': '',
            'completed_tasks': total_unassigned_completed_tasks,
            'total_tasks': total_unassigned_tasks,
        })
        return self.render_to_ok({'milestones': milestones})


class TasksForMilestoneApiView(GenericView):
    @login_required
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
                'ref': issue.ref,
                'id': issue.id,
                'subject': issue.subject,
                'to': issue.assigned_to and issue.assigned_to.first_name or None,
                'to_id': issue.assigned_to and issue.assigned_to.id or None,
                'status': issue.status,
                'status_view': issue.get_status_display(),
                'priority': issue.priority,
                'priority_view': issue.get_priority_display(),
                'type': issue.type,
                'type_view': issue.get_type_display(),
                'edit_url': issue.get_edit_api_url(),
                'drop_url': issue.get_drop_api_url(),
                'asociate_url': issue.get_asoiciate_api_url(),
                'url': issue.get_view_url(),
                'milestone_id': issue.milestone and issue.milestone.id or None,
            }
            response_list.append(response_dict)
        return self.render_to_ok({"tasks": response_list})


class ProjectDeleteApiView(GenericView):
    """ API Method for delete projects. """
    @login_required
    def post(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        project.delete()
        return self.render_to_ok()


class MilestoneCreateApiView(GenericView):
    @login_required
    def post(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        form = forms.MilestoneForm(request.POST)
        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.project = project
            milestone.save()

            context = {
                'name':form.cleaned_data['name'],
                'id': milestone.id,
                'url': milestone.get_tasks_for_milestone_api_url(),
                'date': milestone.estimated_finish or '',
            }
            return self.render_to_ok(context)
        
        return self.render_to_error(form.jquery_errors)


class MilestoneEditApiView(GenericView):
    @login_required
    def post(self, request, pslug, mid):
        project = get_object_or_404(models.Project, slug=pslug)
        milestone = get_object_or_404(project.milestones, pk=mid)

        form = forms.MilestoneForm(request.POST, instance=milestone)
        if form.is_valid():
            milestone = form.save(commit=True)
            return self.render_to_ok({'id':milestone.id})

        return self.render_to_error()
    


class IssueCreateApiView(GenericView):
    @login_required
    def post(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        milestones = project.milestones.all()
        form = forms.IssueForm(request.POST, milestone_queryset=milestones)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.project = project
            issue.save()
            return self.render_to_ok()

        return self.render_to_error(form.jquery_errors)


class IssueEditApiView(GenericView):
    @login_required
    def post(self, request, pslug, iref):
        issue = get_object_or_404(models.Issue, ref=iref, project__slug=pslug)
        milestones = issue.project.milestones.all()
        form = forms.IssueForm(request.POST, instance=issue, milestone_queryset=milestones)
        if form.is_valid():
            issue = form.save()
            return self.render_to_ok()

        return self.render_to_error(form.jquery_errors)

class IssueDropApiView(GenericView):
    @login_required
    def post(self, request, pslug, iref):
        issue = get_object_or_404(models.Issue, ref=iref, project__slug=pslug)
        issue.delete()
        return self.render_to_ok()

class IssueAsociateApiView(GenericView):
    @login_required
    def get(self, request, pslug, iref):
        issue = get_object_or_404(models.Issue, ref=iref, project__slug=pslug)
        try:
            mid = int(request.GET.get('milestone', ''))
        except (ValueError, TypeError):
            return self.render_to_error('invalid paremeters')
        
        if mid == 0:
            issue.milestone = None
            issue.save()
        else:
            issue.milestone = get_object_or_404(models.Milestone, \
                project__slug=pslug, pk=mid)
            issue.save()
        
        return self.render_to_ok()

        

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
