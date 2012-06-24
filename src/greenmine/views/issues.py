# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from django.shortcuts import get_object_or_404
from django.template import loader
from django.db.models import Q

from greenmine.core.generic import GenericView
from greenmine.core.decorators import login_required

from datetime import timedelta
from greenmine import models
from greenmine.forms import base as forms
from greenmine.core.utils import iter_points


class IssueList(GenericView):
    """
    Tasks/Bugs view.
    """

    template_name = 'issues.html'
    menu = ['issues']

    def filter_issues(self, milestone, order_by=None, status=None):
        issues = milestone.tasks.filter(type="bug")

        if status is not None:
            issues = issues.filter(status=status)

        if order_by is None:
            issues = issues.order_by('-created_date')
        else:
            issues = issues.order_by(order_by)

        for issue in issues:
            issue_object = {
                'id': issue.pk,
                'view_url': issue.get_view_url(),
                'delete_url': issue.get_delete_url(),
                'subject': issue.subject,
                'type': issue.get_type_display(),
                'status': issue.get_status_display(),
            }
            if issue.assigned_to:
                issue_object['assigned_to'] = issue.assigned_to.get_full_name()
            else:
                issue_object['assigned_to'] = ugettext(u"Unassigned")

            yield issue_object

    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', 'view'),
            ('task', 'view'),
        ])

        milestones = list(project.milestones.order_by('-created_date'))
        if len(milestones) == 0:
            messages.error(request, _("No milestones found"))
            return self.render_redirect(project.get_backlog_url())

        selected_milestone = milestones[0]
        tasks = self.filter_issues(selected_milestone)

        context = {
            'project': project,
            'milestones': milestones,
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
