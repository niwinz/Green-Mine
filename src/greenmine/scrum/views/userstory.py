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

class UserStoryView(GenericView):
    template_name = "user-story-view.html"

    @login_required
    def get(self, request, pslug, iref):
        """ View US Detail """
        project = get_object_or_404(Project, slug=pslug)
        user_story = get_object_or_404(project.user_stories, ref=iref)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', 'view'),
        ])

        context = {
            'user_story':user_story,
            'milestone':user_story.milestone,
            'project': project,
        }
        return self.render_to_response(self.template_name, context)


class UserStoryCreateView(GenericView):
    template_name = "user-story-create.html"

    @login_required
    def get(self, request, pslug, mid=None):
        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', ('view', 'edit')),
            ('userstory', ('view', 'create')),
        ])

        if mid is not None:
            milestone = get_object_or_404(project.milestones, pk=mid)
        else:
            milestone = None

        form = UserStoryForm(initial={'milestone': milestone})
        context = {
            'form':form,
            'project':project,
        }
        return self.render_to_response(self.template_name, context)

    @login_required
    def post(self, request, pslug, mid=None):
        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', ('view', 'edit')),
            ('userstory', ('view', 'create')),
        ])

        if mid is not None:
            milestone = get_object_or_404(project.milestones, pk=mid)
        else:
            milestone = None

        form = UserStoryForm(request.POST, initial={'milestone': milestone})

        if not form.is_valid():
            return self.render_json_error(form.errors)

        instance = form.save(commit=False)
        instance.milestone = milestone
        instance.owner = request.user
        instance.project = project
        instance.save()

        #TODO: review this save_m2m
        form.save_m2m()

        signals.mail_userstory_created.send(sender=self, us=instance, user=request.user)
        self.create_asociated_tasks(project, instance)

        #messages.info(request, _(u'The user story was created correctly'))
        return self.render_json({"redirect_to": project.get_backlog_url()})

    def create_asociated_tasks(self, project, user_story):
        texts = list(project.get_extras().parse_ustext(user_story.description))
        tasks = []

        for text in texts:
            task = Task(
                user_story=user_story,
                ref = ref_uniquely(project, user_story.__class__),
                description = "",
                project = project,
                milestone = user_story.milestone,
                owner = self.request.user,
                subject = text
            )
            tasks.append(task)

        Task.objects.bulk_create(tasks)

        for task in tasks:
            signals.mail_task_created.send(sender=self,
                task = task, user = self.request.user)


class UserStoryEdit(GenericView):
    template_name = "user-story-edit.html"

    @login_required
    def get(self, request, pslug, iref):
        project = get_object_or_404(Project, slug=pslug)
        user_story = get_object_or_404(project.user_stories, ref=iref)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', ('view', 'edit')),
            ('userstory', ('view', 'edit')),
        ])

        form = UserStoryForm(instance=user_story)
        context = {
            'project': project,
            'user_story': user_story,
            'form': form,
        }
        return self.render_to_response(self.template_name, context)

    @login_required
    def post(self, request, pslug, iref):
        project = get_object_or_404(Project, slug=pslug)
        user_story = get_object_or_404(project.user_stories, ref=iref)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', ('view', 'edit')),
            ('userstory', ('view', 'edit')),
        ])

        form = UserStoryForm(request.POST, instance=user_story)
        if form.is_valid():
            user_story = form.save(commit=True)
            signals.mail_userstory_modified.send(sender=self, us=user_story, user=request.user)
            messages.info(request, _(u'The user story has been successfully saved'))
            return self.render_redirect(user_story.get_view_url())

        context = {
            'project': project,
            'user_story': user_story,
            'form': form,
        }
        return self.render_to_response(self.template_name, context)


class UserStoryDeleteView(GenericView):
    template_name = "user-story-delete.html"

    @login_required
    def post(self, request, pslug, iref):
        project = get_object_or_404(Project, slug=pslug)
        user_story = get_object_or_404(project.user_stories, ref=iref)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', ('view', 'edit')),
            ('userstory', ('view', 'edit', 'delete')),
        ])

        signals.mail_userstory_deleted.send(sender=self, us=user_story, user=request.user)
        user_story.delete()

        return self.render_to_ok()

class AssignUserStory(GenericView):
    """
    Assign user story callback.
    """

    template_name  = "milestone-item.html"

    @login_required
    def post(self, request, pslug, iref):
        if "mid" not in request.POST:
            return self.render_to_error()

        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', ('view', 'edit')),
        ])

        user_story = get_object_or_404(project.user_stories, ref=iref)

        milestone_id = request.POST['mid']
        milestone = get_object_or_404(project.milestones, pk=milestone_id)

        user_story.milestone = milestone
        user_story.save()

        user_story.tasks.update(milestone=milestone)

        context = {
            'us': user_story,
            'project': project,
        }

        return self.render_to_response(self.template_name, context)


class UnassignUserStory(GenericView):
    """
    Unassign callback on backlog.
    """

    template_name = 'user-story-item.html'

    @login_required
    def post(self, request, pslug, iref):
        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', ('view', 'edit')),
        ])

        user_story = get_object_or_404(project.user_stories, ref=iref)
        user_story.milestone = None
        user_story.save()
        user_story.tasks.update(milestone=None)

        context = {'us': user_story, 'project':project}
        return self.render_to_response(self.template_name, context)


class UsFormInline(GenericView):
    """
    Is a inline edit module of user story.
    Main location is in a backlog.
    """

    template_name = 'user-story-form-inline.html'
    us_template_name0 = 'user-story-item.html'
    us_template_name1 = 'milestone-item.html'

    @login_required
    def get(self, request, pslug, iref):
        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', ('view', 'edit')),
        ])

        user_story = get_object_or_404(project.user_stories, ref=iref)

        form = UserStoryFormInline(instance=user_story)
        context = {'form': form}
        return self.render_to_response(self.template_name, context)

    @login_required
    def post(self, request, pslug, iref):
        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', ('view', 'edit')),
        ])

        user_story = get_object_or_404(project.user_stories, ref=iref)

        form = UserStoryFormInline(request.POST, instance=user_story)

        if form.is_valid():
            us = form.save(commit=True)
            context = {
                'us': user_story,
                'project': project,
            }

            response_data = {}
            if us.milestone is not None:
                response_data['action'] = 'assign'
                response_data['html'] = render_to_string(self.us_template_name1, context,
                    context_instance=RequestContext(request))

            else:
                response_data['action'] = 'save'
                response_data['html'] = render_to_string(self.us_template_name0, context,
                    context_instance=RequestContext(request))
            return self.render_to_ok(response_data)

        return self.render_to_error(form.errors)
