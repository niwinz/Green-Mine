# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.template import loader
from django.db.models import Q
from django.db import transaction

from greenmine.core.generic import GenericView
from greenmine.core.decorators import login_required

from datetime import timedelta
from greenmine import models
from greenmine.forms import base as forms
from greenmine.core.utils import iter_points

from greenmine.forms.issues import IssueFilterForm, IssueCreateForm
from greenmine.forms.base import CommentForm


class IssueList(GenericView):
    """
    Issues list view.
    """

    template_name = 'issues.html'
    menu = ['issues']

    def get_query_set(self, milestone):
        return milestone.tasks.filter(type="bug")

    def filter_issues(self, milestone, order_by=None, status=None):
        issues = self.get_query_set(milestone)

        if status is not None:
            issues = issues.exclude(status=status)

        if order_by is None:
            issues = issues.order_by('-created_date')
        else:
            issues = issues.order_by(order_by)

        return (issue.to_dict() for issue in issues)

    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        milestone_pk = request.GET.get('milestone', None)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', 'view'),
            ('task', 'view'),
        ])

        milestones = project.milestones.order_by('-created_date')
        if len(milestones) == 0:
            messages.error(request, _("No milestones found"))
            return self.render_redirect(project.get_backlog_url())

        if milestone_pk:
            selected_milestone = get_object_or_404(milestones, pk=milestone_pk)
        else:
            selected_milestone = milestones[0]

        tasks = self.filter_issues(selected_milestone, status="closed")

        context = {
            'project': project,
            'milestones': list(milestones),
            'milestone': selected_milestone,
            'tasks': tasks,
        }

        return self.render_to_response(self.template_name, context)

    @login_required
    def post(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', 'view'),
            ('task', 'view'),
        ])

        form = IssueFilterForm(request.POST, project=project)
        if not form.is_valid():
            return self.render_to_error(form.errors)

        milestone = form.cleaned_data['milestone']
        status = form.cleaned_data['status'] or None
        order_by = form.cleaned_data['order_by']

        filtered_tasks = list(self.filter_issues(milestone, order_by, status))

        return self.render_to_ok({
            "tasks": filtered_tasks,
        })


class CreateIssue(GenericView):
    template_name = "issues-create.html"

    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)

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
        project = get_object_or_404(models.Project, slug=pslug)

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


class EditIssue(GenericView):
    template_name = "issues-edit.html"

    @login_required
    def get(self, request, pslug, tref):
        project = get_object_or_404(models.Project, slug=pslug)
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
        project = get_object_or_404(models.Project, slug=pslug)

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
        project = get_object_or_404(models.Project, slug=pslug)
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
        project = get_object_or_404(models.Project, slug=pslug)
        task = get_object_or_404(project.tasks, ref=tref)

        form = CommentForm(request.POST, request.FILES)

        if not form.is_valid():
            return self.render_to_error(form.errors)

        change_instance = models.Change.objects.create(
            change_type = models.TASK_COMMENT,
            owner = request.user,
            content_object = task,
            project = project,
            data = {'comment': form.cleaned_data['description']},
        )

        if "attached_file" in form.cleaned_data:
            change_attachment = models.ChangeAttachment.objects.create(
                owner = request.user,
                change = change_instance,
                attached_file = form.cleaned_data['attached_file'],
            )

        html = loader.render_to_string("issues-view-change-part.html", {
            "change": change_instance,
            "project": project,
        })

        return self.render_to_ok({"html":html})
