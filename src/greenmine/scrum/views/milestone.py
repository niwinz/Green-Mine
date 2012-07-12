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

class MilestoneCreateView(GenericView):
    template_name = 'milestone-create.html'
    menu = []

    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', ('view', 'edit', 'create')),
        ])

        form = MilestoneForm(initial={'estimated_start': now()})
        context = {
            'form': form,
            'project': project,
        }

        return self.render_to_response(self.template_name, context)

    @login_required
    def post(self, request, pslug):
        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', ('view', 'create')),
        ])

        form = MilestoneForm(request.POST)

        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.project = project
            milestone.owner = request.user
            milestone.save()

            signals.mail_milestone_created\
                .send(sender=self, milestone=milestone, user=request.user)

            return self.render_redirect(project.get_backlog_url())

        context = {
            'form': form,
            'project': project,
        }
        return self.render_to_response(self.template_name, context)


class MilestoneEditView(GenericView):
    template_name = 'milestone-edit.html'
    menu = []

    @login_required
    def get(self, request, pslug, mid):
        project = get_object_or_404(Project, slug=pslug)
        milestone = get_object_or_404(project.milestones, pk=mid)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', ('view', 'edit', 'create')),
        ])

        form = MilestoneForm(instance=milestone)

        context = {
            'form': form,
            'project': project,
            'milestone': milestone,
        }

        return self.render_to_response(self.template_name, context)

    @login_required
    def post(self, request, pslug, mid):
        project = get_object_or_404(Project, slug=pslug)
        milestone = get_object_or_404(project.milestones, pk=mid)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', ('view', 'create')),
        ])

        form = MilestoneForm(request.POST, instance=milestone)

        if form.is_valid():
            milestone = form.save(commit=True)

            signals.mail_milestone_modified.send(sender=self,
                milestone = milestone, user = request.user)

            messages.info(request, _(u"Milestone saved successful."))
            return self.render_redirect(project.get_backlog_url())

        context = {
            'form': form,
            'project': project,
        }
        return self.render_to_response(self.template_name, context)


class MilestoneDeleteView(GenericView):
    def post(self, request, pslug, mid):
        project = get_object_or_404(Project, slug=pslug)
        milestone = get_object_or_404(project.milestones, pk=mid)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', ('view', 'delete')),
        ])

        signals.mail_milestone_deleted.send(sender=self,
            milestone = milestone, user = request.user)

        # update all user stories, set milestone to None
        milestone.user_stories.all().update(milestone=None)

        # update all tasks with user story, set milestone to None
        milestone.tasks.filter(user_story__isnull=False).update(milestone=None)

        # delete all tasks without user story
        milestone.tasks.filter(user_story__isnull=True).delete()

        milestone.delete()

        return self.render_to_ok()
