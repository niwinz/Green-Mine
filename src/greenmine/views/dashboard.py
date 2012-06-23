# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404

from greenmine.core.generic import GenericView
from greenmine.core.decorators import login_required

from datetime import timedelta
from greenmine import models
from greenmine.forms import base as forms

class MilestoneBurndownView(GenericView):
    @login_required
    def get(self, request, pslug, mid):
        project = get_object_or_404(models.Project, slug=pslug)
        milestone = get_object_or_404(project.milestones, pk=mid)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', 'view'),
        ])

        points_done_on_date = [];
        date = milestone.estimated_start

        while date <= milestone.estimated_finish:
            points_done_on_date.append(milestone.get_points_done_at_date(date))
            date = date + timedelta(days=1)
        points_done_on_date.append(milestone.get_points_done_at_date(date))

        context = {
            'points_done_on_date': points_done_on_date,
            'sprint_points': milestone.total_points,
            'begin_date': milestone.estimated_start,
            'end_date': milestone.estimated_finish,
        }

        return self.render_to_ok(context)


class DashboardView(GenericView):
    template_name = 'dashboard.html'
    menu = ['dashboard']

    @login_required
    def get(self, request, pslug, mid=None):
        project = get_object_or_404(models.Project, slug=pslug)

        try:
            milestones = project.milestones.order_by('-created_date')
            milestone = milestones.get(pk=mid) if mid is not None else milestones[0]
        except IndexError:
            messages.error(request, _("No milestones found"))
            return self.render_redirect(project.get_backlog_url())

        if mid is None:
            return self.render_redirect(milestone.get_dashboard_url())

        form = forms.TaskForm(project=project, initial={'milestone':milestone})

        context = {
            'user_stories':milestone.user_stories.order_by('-priority', 'subject'),
            'milestones': milestones,
            'milestone':milestone,
            'project': project,
            'status_list': models.TASK_STATUS_CHOICES,
            'participants': project.all_participants,
            'form': form,
        }
        return self.render_to_response(self.template_name, context)

