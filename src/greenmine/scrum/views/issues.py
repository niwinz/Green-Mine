# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.template import loader
from django.db.models import Q
from django.db import transaction
from django.contrib import messages

from greenmine.core.generic import GenericView
from greenmine.core.decorators import login_required

from datetime import timedelta
from greenmine.forms import base as forms
from greenmine.core.utils import iter_points

from greenmine.scrum.forms.issues import IssueFilterForm, IssueCreateForm
from greenmine.forms.base import CommentForm
from greenmine.scrum.models import *
from greenmine.taggit.models import Tag

class IssueList(GenericView):
    """
    Issues list view.
    """

    template_name = 'issues.html'
    menu = ['issues']

    def get_general_context(self, project):
        participants = [{
            "name": x.get_full_name(),
            "id": x.id,
        } for x in project.all_participants]

        statuses = [{
            "name": x[1],
            "id": x[0]
        } for x in TASK_STATUS_CHOICES]

        return {
            "participants": [{'name': ugettext("Unassigned"), "id":""}] + participants,
            "statuses": statuses,
        }

    def initialize(self, request):
        self.check_role(request.user, self.project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', 'view'),
            ('task', 'view'),
        ])

        form = IssueFilterForm(request.GET, project=self.project)
        self.valid_form = form.is_valid()
        if self.valid_form:
            milestone = form.cleaned_data['milestone']
            status = form.cleaned_data['status']
            order_by = form.cleaned_data['order_by']
            tags = form.cleaned_data['tags']
            assigned_to = form.cleaned_data['assigned_to']

            tasks_and_filters = self.project.tasks.filter(type='bug').\
                filter_and_build_filter_dict(milestone, status, tags, assigned_to)

            self.tasks = tasks_and_filters['list']
            self.filter_dict = tasks_and_filters['filters']

        else:
            messages.error(request, _("Uops!, something went wrong!"))
            self.tasks = []
            self.filter_dict = {}

    @login_required
    def get(self, request, pslug):
        self.project = get_object_or_404(Project, slug=pslug)
        self.initialize(request)

        _aditional_context = self.get_general_context(self.project)

        if request.is_ajax():
            if not self.valid_form:
                return self.render_to_error(form.errors)

            context = {
                "tasks": [task.to_dict() for task in self.tasks],
                'filter_dict': self.filter_dict,
            }
            context.update(_aditional_context)
            return self.render_to_ok(context)

        else:
            context = {
                'project': self.project,
                'tasks': (task.to_dict() for task in self.tasks),
                'filter_dict': self.filter_dict,
            }

            context.update(_aditional_context)
            return self.render_to_response(self.template_name, context)


class CreateIssue(GenericView):
    template_name = "issues-create.html"

    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', 'view'),
            ('task', ('view', 'create')),
        ])

        initial_data = {
            "milestone": request.GET.get('milestone', None),
        }

        form = IssueCreateForm(project=project, initial=initial_data)

        return self.render_to_response(self.template_name, {
            "form": form,
            "project": project,
        })

    @login_required
    def post(self, request, pslug):
        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', 'view'),
            ('task', ('view', 'create')),
        ])

        initial_data = {
            "milestone": request.GET.get('milestone', None),
        }
        form = IssueCreateForm(request.POST, project=project, initial=initial_data)
        if not form.is_valid():
            return self.render_json_error(form.errors)

        issue = form.save(commit=False)
        issue.type = 'bug'
        issue.project = project
        issue.owner = request.user
        issue.save()
        form.save_m2m()

        redirect_to = reverse('issues-list', args=[project.slug]) \
            + "?milestone={0}".format(issue.milestone.pk)

        return self.render_to_ok({"task": issue.to_dict(), 'redirect_to':redirect_to})


class EditIssue(GenericView):
    template_name = "issues-edit.html"

    @login_required
    def get(self, request, pslug, tref):
        project = get_object_or_404(Project, slug=pslug)
        issue = get_object_or_404(project.tasks, ref=tref)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', 'view'),
            ('task', ('view', 'create')),
        ])

        form = IssueCreateForm(project=project, instance=issue)
        return self.render_to_response(self.template_name, {
            "form": form,
            "project": project,
        })

    @login_required
    def post(self, request, pslug):
        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', 'view'),
            ('task', ('view', 'create')),
        ])

        initial_data = {
            "milestone": request.GET.get('milestone', None),
        }
        form = IssueCreateForm(request.POST, project=project, initial=initial_data)
        if not form.is_valid():
            return self.render_json_error(form.errors)

        issue = form.save(commit=False)
        issue.type = 'bug'
        issue.project = project
        issue.owner = request.user
        issue.save()

        redirect_to = reverse('issues-list', args=[project.slug]) \
            + "?milestone={0}".format(issue.milestone.pk)

        return self.render_to_ok({"task": issue.to_dict(), 'redirect_to':redirect_to})


class IssueView(GenericView):
    template_name = "issues-view.html"
    menu = ['issues']

    @login_required
    def get(self, request, pslug, tref):
        project = get_object_or_404(Project, slug=pslug)
        task = get_object_or_404(project.tasks.filter(type="bug"), ref=tref)

        form = CommentForm()

        context = {
            'form': form,
            'task': task,
            'project': project,
        }

        return self.render_to_response(self.template_name, context)


class IssueSendComment(GenericView):
    @login_required
    @transaction.commit_on_success
    def post(self, request, pslug, tref):
        project = get_object_or_404(Project, slug=pslug)
        task = get_object_or_404(project.tasks, ref=tref)

        form = CommentForm(request.POST, request.FILES)

        if not form.is_valid():
            return self.render_to_error(form.errors)

        change_instance = Change.objects.create(
            change_type = TASK_COMMENT,
            owner = request.user,
            content_object = task,
            project = project,
            data = {'comment': form.cleaned_data['description']},
        )

        if "attached_file" in form.cleaned_data:
            change_attachment = ChangeAttachment.objects.create(
                owner = request.user,
                change = change_instance,
                attached_file = form.cleaned_data['attached_file'],
            )

        html = loader.render_to_string("issues-view-change-part.html", {
            "change": change_instance,
            "project": project,
        })

        return self.render_to_ok({"html":html})
