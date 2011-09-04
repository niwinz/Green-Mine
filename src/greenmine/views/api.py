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
import datetime


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
            total_tasks = ml.uss.count()
            milestones.append({
                'id': ml.id,
                'url': ml.get_tasks_for_milestone_api_url(),
                'edit_url': ml.get_edit_api_url(),
                'name': ml.name,
                'estimated_finish': ml.estimated_finish and \
                    ml.estimated_finish.strftime('%d/%m/%Y') or '',
                'completed_tasks': 0,
                'total_tasks': total_tasks,
                'detail_url': ml.get_ml_detail_url(),
            })

        total_unassigned_tasks = project.uss.filter(milestone__isnull=True).count()

        milestones.append({
            'id': 0,
            'url': ml.project.get_unasigned_tasks_api_url(),
            'edit_url': '',
            'name': _('Unasigned'),
            'estimated_finish': '',
            'completed_tasks': 0,
            'total_tasks': total_unassigned_tasks,
        })

        return self.render_to_ok({'milestones': milestones})


class UsForMilestoneApiView(GenericView):
    @login_required
    def get(self, request, pslug, mid=None):
        project = get_object_or_404(models.Project, slug=pslug)
        
        uss = models.Us.objects.none()
        if mid:
            try:
                milestone = project.milestones.get(pk=mid)
                uss = milestone.uss.all()
            except models.Milestone.DoesNotExist:
                return self.render_to_error("milestone does not exists")
        else:
            uss = project.uss.filter(milestone__isnull=True)
        
        #: TODO: future set from user-project-settings relation table.
        uss = uss.order_by('-priority')

        response_list = []
        for us in uss:
            response_dict = {
                'ref': us.ref,
                'id': us.id,
                'subject': us.subject,
                'to': 'No use mas este campo',
                'to_id': None,
                'priority': us.priority,
                'priority_view': us.get_priority_display(),
                'edit_url': us.get_edit_api_url(),
                'drop_url': us.get_drop_api_url(),
                'asociate_url': us.get_asoiciate_api_url(),
                'url': us.get_view_url(),
                'milestone': us.milestone and us.milestone.id or None,
                'tasks': us.tasks.count(),
                'status': us.status,
                'status_view': us.get_status_display(),
                'estimation': us.points,
                'description': us.description,
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
    


class UsCreateApiView(GenericView):
    @login_required
    def post(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        milestones = project.milestones.all()
        form = forms.UsForm(request.POST, milestone_queryset=milestones)
        if form.is_valid():
            us = form.save(commit=False)
            us.project = project
            us.save()

            html = loader.render_to_string('modules/user-story-dashboard.html', 
                {'us':us}, context_instance=RequestContext(request))

            return self.render_to_ok({'html':html})

        return self.render_to_error(form.jquery_errors)


class UsEditApiView(GenericView):
    @login_required
    def post(self, request, pslug, iref):
        us = get_object_or_404(models.Us, ref=iref, project__slug=pslug)
        milestones = us.project.milestones.all()
        form = forms.UsForm(request.POST, instance=us, milestone_queryset=milestones)
        if form.is_valid():
            us = form.save()
            return self.render_to_ok()

        return self.render_to_error(form.jquery_errors)


class UsDropApiView(GenericView):
    @login_required
    def post(self, request, pslug, iref):
        us = get_object_or_404(models.Us, ref=iref, project__slug=pslug)
        us.childs.all().delete()
        us.delete()
        return self.render_to_ok()


class UsAsociateApiView(GenericView):
    """ Asociate user story with one milestone. """
    @login_required
    def get(self, request, pslug, iref):
        us = get_object_or_404(models.Us, ref=iref, project__slug=pslug)
        try:
            mid = int(request.GET.get('milestone', ''))
        except (ValueError, TypeError):
            return self.render_to_error('invalid paremeters')
        
        if mid == 0:
            us.milestone = None
        else:
            us.milestone = get_object_or_404(models.Milestone, \
                project__slug=pslug, pk=mid)

        us.tasks.update(milestone=us.milestone)
        us.save()
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


class TaskAlterApiView(GenericView):
    """ Api view for alter task status, priority and other 
    minor modifications. """

    def post(self, request, pslug, mid, taskref):
        project = get_object_or_404(models.Project, slug=pslug)
        milestone = get_object_or_404(project.milestones, pk=mid)
        task = get_object_or_404(milestone.tasks, ref=taskref)
        us = get_object_or_404(milestone.uss, pk=request.POST.get('us',None))

        mf = request.POST.get('modify_flag', '')
        if mf not in ['close', 'progress', 'new']:
            return self.render_to_error()

        # mark old us modified
        if task.us and task.us != us:
            task.us.modified_date = datetime.datetime.now()

        task.us = us
        
        if mf == 'close':
            task.status = 'completed'
        elif mf == 'progress':
            task.status = 'progress'
        else:
            task.status = 'open'

        task.save()
        
        # automatic control of user story status.
        if us.tasks.filter(status__in=['closed','completed']).count() == us.tasks.all().count():
            us.status = 'completed'
        elif us.tasks.all().count() == us.tasks.filter(status='open').count():
            us.status = 'open'
        else:
            us.status = 'progress'

        us.save()
        return self.render_to_ok()
 

class TaskCreateApiView(GenericView):
    @login_required
    def post(self, request, pslug, mid):
        project = get_object_or_404(models.Project, slug=pslug)
        milestone = get_object_or_404(project.milestones, pk=mid)
        
        form = forms.TaskForm(request.POST,
            us_qs=milestone.uss.all(),
            assignedto_qs=project.participants.all()
        )

        if form.is_valid():
            task = form.save(commit=False)
            task.owner = request.user
            task.project = project
            task.milestone = milestone
            task.save()
            
            html = loader.render_to_string('modules/task-user-story.html',
                {'task': task}, context_instance=RequestContext(request))

            return self.render_to_ok({'html':html, 'us': task.us.id})

        return self.render_to_error(form.errors)


class TaskReasignationsApiView(GenericView):
    def get(self, request, pslug, mid, taskref):
        project = get_object_or_404(models.Project, slug=pslug)
        milestone = get_object_or_404(project.milestones, pk=mid)
        task = get_object_or_404(milestone.tasks, ref=taskref)
        
        userid = request.GET.get('userid', '')
        if not userid:
            print userid
            task.assigned_to = None
        else:
            print userid
            task.assigned_to = get_object_or_404(project.participants, pk=userid)

        task.save()
        return self.render_to_ok()


""" Statistics Views """

class MilestoneStatsApiView(GenericView):
    def get(self, request, pslug, mid):
        project = get_object_or_404(models.Project, slug=pslug)
        milestone = get_object_or_404(project.milestones, pk=mid)
        
        total_tasks = milestone.tasks.all().count()
        total_sum = sum([2 if x.status in ['completed', 'closed'] else 1 \
            for x in milestone.tasks.exclude(status='open')])

        value = (total_sum * 100)/(total_tasks*2)
        
        return self.render_to_ok({'ts': total_sum, 't': total_tasks, 'v':value})
