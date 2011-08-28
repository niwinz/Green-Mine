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
from django.db.models import Q

import logging, re
logger = logging.getLogger('greenmine')

from greenmine.models import *
from greenmine.forms import LoginForm
from greenmine.utils import encrypt_password
from greenmine.views.decorators import login_required
from greenmine.views.generic import GenericView

class ApiLogin(GenericView):
    def post(self, request):
        login_form = LoginForm(request.POST, request = request)
        if not login_form.is_valid():
            return self.render_to_error(login_form.jquery_errors)

        request.session['current_user_id'] = login_form._user.id
        return self.render_to_ok({'userid': login_form._user.id, 'redirect_to': '/'})


class UserListApiView(GenericView):
    def get(self, request):
        if "term" not in request.GET:
            return self.render_to_ok({'list':[]})
        
        term = request.GET['term']
        users = User.objects.filter(
            Q(username__istartswith=term) | Q(first_name__istartswith=term)
        )
        context = {'list': [{'id':x.id, 'label':x.first_name, 'value':x.first_name,
            'gravatar':'/static/auxiliar/imgs/gravatar.jpg'} for x in users]}
        return self.render_to_ok(context)


class TasksForMilestoneApiView(GenericView):
    def get(self, request, pslug, mid=None):
        project = get_object_or_404(Project, slug=pslug)
        
        issues = Issue.objects.none()
        if mid:
            try:
                milestone = project.milestones.get(pk=mid)
                issues = milestone.issues.all()
            except Milestone.DoesNotExists:
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
            }
            response_list.append(response_dict)
        return self.render_to_ok({"tasks": response_list})


class ProjectDeleteApiView(GenericView):
    """ API Method for delete projects. """
    def post(self, request, pslug):
        project = get_object_or_404(Project, slug=pslug)
        project.delete()
        return self.render_to_ok()


from greenmine.forms import MilestoneCreateForm

class MilestoneCreateApiView(GenericView):
    def post(self, request, pslug):
        project = get_object_or_404(Project, slug=pslug)
        form = MilestoneCreateForm(request.POST)
        if form.is_valid():
            print form.cleaned_data
            milestone = Milestone.objects.create(
                name = form.cleaned_data['name'],
                project = project,
            )
            context = {
                'name':form.cleaned_data['name'],
                'id': milestone.id,
                'milestoneurl': milestone.get_tasks_for_milestone_api_url(),
                'date': milestone.estimated_finish or '',
            }
            return self.render_to_ok(context)
        
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
            
