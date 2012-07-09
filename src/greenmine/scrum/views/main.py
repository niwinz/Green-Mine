# -*- coding: utf-8 -*-

from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest, Http404
from django.core.cache import cache
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.core.mail import EmailMessage
from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.template import RequestContext, loader
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.utils import IntegrityError
from django.db import transaction
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.utils.timezone import now

from django.views.decorators.csrf import ensure_csrf_cookie

from greenmine.core.generic import GenericView
from greenmine.core.decorators import login_required, staff_required

# Temporal imports
from greenmine.base.models import *
from greenmine.scrum.models import *

from greenmine.forms.base import *
from greenmine.questions.forms import *
from greenmine.scrum.forms.project import *
from greenmine.scrum.forms.milestone import *
from greenmine.core.utils import iter_points
from greenmine.core import signals

import os
import re

from datetime import timedelta

class HomeView(GenericView):
    """
    General user projects view. This is a home page.
    """

    template_name = 'projects.html'
    menu = ['projects']

    @login_required
    def get(self, request, *args, **kwargs):
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1

        if request.user.is_staff:
            projects = Project.objects.all()
        else:
            projects = request.user.projects.all() | \
                request.user.projects_participant.all()

        projects = projects.order_by('name').distinct()
        paginator = Paginator(projects, 20)
        page = paginator.page(page)

        context = {
            'is_paginated': True if paginator.count else False,
            'page': page,
            'projects': projects,
        }
        return self.render_to_response(self.template_name, context)



class SendRecoveryPasswordView(GenericView):
    """
    Staff's method for send recovery password.
    """

    @login_required
    @staff_required
    def get(self, request, uid):
        user = get_object_or_404(User.objects.select_for_update(), pk=uid)
        user.set_unusable_password()
        user.save()

        signals.mail_recovery_password.send(sender=self, user=user)
        messages.info(request, _(u"Recovery password email are sended"))

        referer = request.META.get('HTTP_REFERER', reverse('users-edit', args=[uid]))
        return self.render_redirect(referer)








class TaskCreateView(GenericView):
    template_name = 'task-create.html'

    menu = ["tasks"]

    @login_required
    def get(self, request, pslug, usref=None, mid=None):
        project = get_object_or_404(Project, slug=pslug)

        if usref is not None and mid is not None:
            return HttpResponseBadRequest()

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', 'view'),
            ('task', ('view', 'create')),
        ])

        if usref is not None:
            user_story = get_object_or_404(project.user_stories, ref=usref)
            milestone = user_story.milestone
        elif mid is not None:
            user_story = None
            milestone = get_object_or_404(project.milestones, pk=mid)
        else:
            return HttpResponseBadRequest()

        form = TaskForm(project=project,
            initial={'milestone':milestone, 'user_story': user_story})

        context = {
            'project': project,
            'form': form,
        }
        return self.render_to_response(self.template_name, context)

    @login_required
    def post(self, request, pslug, usref=None, mid=None):
        project = get_object_or_404(Project, slug=pslug)

        if usref is None and mid is None:
            return HttpResponseBadRequest()

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', 'view'),
            ('task', ('view', 'create')),
        ])

        if usref is not None:
            user_story = get_object_or_404(project.user_stories, ref=usref)
            milestone = user_story.milestone
        elif mid is not None:
            user_story = None
            milestone = get_object_or_404(project.milestones, pk=mid)
        else:
            return HttpResponseBadRequest()

        form = TaskForm(request.POST, project=project,
            initial={'milestone':milestone, 'user_story': user_story})

        next_url = request.GET.get('next', None)
        _from = request.POST.get('from', '')

        if form.is_valid():
            task = form.save(commit=False)
            task.owner = request.user
            task.project = project
            task.save()

            signals.mail_task_created.send(sender=self, task=task, user=request.user)

            if task.assigned_to != None:
                signals.mail_task_assigned.send(sender=self, task=task, user=request.user)

            if _from == 'dashboard':
                return self.create_response_for_dashboard(form, task, project)

            messages.info(request, _(u"The task has been created with success!"))
            response = {}

            if next_url:
                response['redirect_to'] = next_url
            else:
                response['redirect_to'] = task.milestone.get_tasks_url()

            return self.render_json(response)

        return self.render_json_error(form.errors)

    def create_response_for_dashboard(self, form, task, project):
        html = loader.render_to_string("dashboard-userstory-task.html", {
            'task':task,
            'project': project,
            'participants': project.all_participants,
            'status_list': TASK_STATUS_CHOICES,
        })

        response = {
            'html': html,
            'status': task.status,
            'userStory': task.user_story.id if task.user_story else None,
        }

        return self.render_json(response)




class Documents(GenericView):
    template_path = 'documents.html'
    menu = ['documents']

    # TODO: fix permissions

    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
        ])

        documents = project.documents.order_by('-created_date')

        context = {
            'documents': documents,
            'project': project,
            'form': DocumentForm(),
        }

        return self.render_to_response(self.template_path, context)

    @login_required
    def post(self, request, pslug):
        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
        ])

        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = Document.objects.create(
                title = form.cleaned_data['title'],
                owner = request.user,
                project = project,
                attached_file = form.cleaned_data['document'],
            )

            html = loader.render_to_string("documents-item.html",
                {'doc': document})

            return self.render_to_ok({'html': html})

        return self.render_json_error(form.errors)


class UserList(GenericView):
    template_path = 'config/users.html'
    menu = ['users']

    @login_required
    @staff_required
    def get(self, request):
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1

        users = User.objects.all()
        paginator = Paginator(users, 20)
        page = paginator.page(page)

        context = {
            'is_paginated': True if paginator.count else False,
            'page': page,
            'users': users,
        }
        return self.render_to_response(self.template_path, context)


class UserView(GenericView):
    template_path = 'config/users-view.html'
    menu = ['users']

    @login_required
    @staff_required
    def get(self, request, uid):
        user = get_object_or_404(User, pk=uid)
        context = {
            'uobj': user,
        }
        return self.render_to_response(self.template_path, context)


class UserCreateView(GenericView):
    template_path = 'config/users-create.html'
    menu = ['users']

    @login_required
    @staff_required
    def get(self, request):
        form = UserEditForm()
        context = {'form': form}
        return self.render_to_response(self.template_path, context)

    @login_required
    @staff_required
    def post(self, request):
        form = UserEditForm(request.POST)
        if form.is_valid():
            user = form.save(commit=True)
            return self.render_redirect(reverse('users-view', args=[user.id]))

        context = {'form': form}
        return self.render_to_response(self.template_path, context)


class UserEditView(GenericView):
    template_path = 'config/users-edit.html'
    menu = ['users']

    @login_required
    @staff_required
    def get(self, request, uid):
        user = get_object_or_404(User, pk=uid)
        form = UserEditForm(instance=user)

        context = {
            'uobj': user,
            'form': form,
        }
        return self.render_to_response(self.template_path, context)

    @login_required
    @staff_required
    def post(self, request, uid):
        user = get_object_or_404(User, pk=uid)
        form = UserEditForm(request.POST, instance=user)

        if form.is_valid():
            form.save()
            messages.info(request, _(u"User saved succesful"))
            return self.render_redirect(reverse('users-edit', args=[user.id]))

        contex = {
            'uobj': user,
            'form': form,
        }
        return self.render_to_response(self.template_path, context)


class UserDelete(GenericView):
    template_path = 'config/users-delete.html'
    menu = ['users']

    def get_context(self):
        user = get_object_or_404(User, pk=self.kwargs['uid'])
        return {'uobj':user}

    @login_required
    @staff_required
    def get(self, request, uid):
        context = self.get_context()
        return self.render_to_response(self.template_path, context)

    @login_required
    @staff_required
    def post(self, request, uid):
        context = self.get_context()
        context['uobj'].delete()
        return self.render_redirect(reverse('users'))


