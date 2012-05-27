# -*- coding: utf-8 -*-

from django.views.decorators.cache import cache_page
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
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
from django.utils.timezone import now
from django.views.generic import TemplateView, RedirectView, View
from django.db.models import Q
from django_gravatar.helpers import get_gravatar_url, has_gravatar

import logging, re
logger = logging.getLogger('greenmine')

from greenmine.models import *
from greenmine import models, forms, utils
from greenmine.views.decorators import login_required
from greenmine.views.generic import GenericView


from django.core.cache import cache
import uuid

class UserListApiView(GenericView):
    """
    Autocomplete helper for project create/edit.
    This autocompletes and searches users by term.
    """

    @login_required
    def get(self, request):
        if "term" not in request.GET:
            return self.render_to_ok({'list':[]})
        
        term = request.GET['term']
        users = models.User.objects.filter(
            Q(username__istartswith=term) | Q(first_name__istartswith=term) | Q(last_name__istartswith=term)
        )
        users_list = []

        for user in users:
            users_list_item = {}
            users_list_item['id'] = user.id
            full_name = user.get_full_name()
            if full_name:
                users_list_item['label'] = full_name
                users_list_item['value'] = full_name
            else:
                users_list_item['label'] = user.username
                users_list_item['value'] = user.username

            if user.get_profile().photo:
                users_list_item['gravatar'] = user.get_profile().photo.url
            else:
                users_list_item['gravatar'] = get_gravatar_url(user.email, size=30)

            users_list.append(users_list_item)

        context = {'list': users_list}
        return self.render_to_ok(context)


class I18NLangChangeApiView(GenericView):
    """ 
    View for set language.
    """

    def get(self, request):
        if 'lang' in request.GET and request.GET['lang'] \
                                    in dict(settings.LANGUAGES).keys():
            request.session['django_language'] = request.GET['lang']
            if request.META.get('HTTP_REFERER', ''):
                return HttpResponseRedirect(request.META['HTTP_REFERER'])
            elif "next" in request.GET and request.GET['next']:
                return HttpResponseRedirect(request.GET['next'])
        
        return HttpResponseRedirect('/')


class TaskAlterApiView(GenericView):
    """ 
    Api view for alter task status, priority and other 
    minor modifications. 
    This is used on dashboard drag and drop.
    """
    
    @login_required
    def post(self, request, pslug, taskref):
        project = get_object_or_404(models.Project, slug=pslug)
        task = get_object_or_404(project.tasks, ref=taskref)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', ('view')),
            ('userstory', ('view', 'edit')),
            ('task', ('view', 'edit')),
        ])
        
        status = request.POST.get('status', '')
        if status not in dict(TASK_STATUS_CHOICES).keys():
            return self.render_to_error({"error_message": "invalid status"})

        task.status, us = status, None
        us_for_update = []

        if "us" in request.POST:
            us_pk = request.POST['us']
            
            if len(us_pk.strip()) == 0:
                if task.user_story:
                    us_for_update.append(task.user_story)
                task.user_story = None

            else:
                try:
                    queryset = models.UserStory.objects.filter(pk=request.POST['us'])
                except ValueError:
                    queryset = models.UserStory.objects.none()

                us = len(queryset) == 1 and queryset.get() or None

            if us:
                task.user_story = us
                us_for_update.append(us)

        task.save()

        for us in set(us_for_update):
            # automatic control of user story status.
            total_tasks_count = us.tasks.count()

            if us.tasks.filter(status__in=['closed','completed']).count() == total_tasks_count:
                us.status = 'completed'
            elif us.tasks.filter(status='open').count() == total_tasks_count:
                us.status = 'open'
            else:
                us.status = 'progress'

            us.modified_date = now()
            us.save()
        
        return self.render_to_ok()
 

class TaskReasignationsApiView(GenericView):
    @login_required
    def post(self, request, pslug, taskref):
        project = get_object_or_404(models.Project, slug=pslug)
        task = get_object_or_404(project.tasks, ref=taskref)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', ('view')),
            ('userstory', ('view', 'edit')),
            ('task', ('view', 'edit')),
        ])
        
        userid = request.POST.get('userid', '')
        if not userid:
            task.assigned_to = None
            task.save()
            return self.render_to_ok()
        
        queryset = project.all_participants.filter(pk=userid)
        user = len(queryset) == 1 and queryset.get() or None

        if user is None:
            return self.render_to_error()

        task.assigned_to = user
        task.save()
        return self.render_to_ok()
