# -*- coding: utf-8 -*-
from django.utils.translation import ugettext
from django.shortcuts import get_object_or_404
from django.db import transaction

from greenmine.core.generic import GenericView
from greenmine.core.decorators import login_required

from datetime import timedelta
from greenmine import models

from ..forms.dashboard import ApiForm as DashboardApiForm

# TODO:
# * quick task creation

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

    def get_general_context(self, project):
        participants = [{
            "name": x.get_full_name(),
            "id": x.id,
        } for x in project.all_participants]

        statuses = [{
            "name": x[1],
            "id": x[0]
        } for x in models.TASK_STATUS_CHOICES]

        return {
            "participants": [{'name': ugettext("Unassigned"), "id":""}] + participants,
            "statuses": statuses,
        }

    @login_required
    def get(self, request, pslug, mid=None):
        project = get_object_or_404(models.Project, slug=pslug)

        try:
            milestones = project.milestones.order_by('-created_date')
            milestone = milestones.get(pk=mid) if mid is not None else milestones[0]
        except IndexError:
            messages.error(request, _("No milestones found"))
            return self.render_redirect(project.get_backlog_url())

        user_stories = [x.to_dict() for x in
            milestone.user_stories.order_by('-priority', 'subject')]

        tasks = [x.to_dict() for x in
            models.Task.objects.filter(type="task", user_story__pk__in=[y['id'] for y in user_stories])]

        context = {
            'user_stories': user_stories,
            'tasks': tasks,
            'milestone':milestone,
            'project': project,
        }

        context.update(self.get_general_context(project))
        return self.render_to_response(self.template_name, context)


class DashboardApiView(GenericView):
    @transaction.commit_on_success
    @login_required
    def post(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', ('view')),
            ('userstory', ('view', 'edit')),
            ('task', ('view', 'edit')),
        ])

        form = DashboardApiForm(request.POST)
        if not form.is_valid():
            return self.render_json_error(form.errors)

        if "task" not in form.cleaned_data or not form.cleaned_data['task']:
            return self.render_json({"messages": ["task parameter is mandatory"]}, ok=False)

        try:
            task = project.tasks.get(pk=form.cleaned_data['task'])
        except models.Task.DoesNotExist:
            return self.render_json({"messages": ["task does not exists"]}, ok=False)

        if "us" in form.cleaned_data and form.cleaned_data['us']:
            try:
                userstory = project.user_stories.get(pk=form.cleaned_data['us'])
            except models.UserStory.DoesNotExist:
                return self.render_json({"messages": ["user story does not exists"]}, ok=False)

            task.user_story = userstory
            task.save()

        if "assignation" in form.cleaned_data:
            if not form.cleaned_data["assignation"]:
                task.assigned_to = None
                task.save()
            else:
                try:
                    person = project.all_participants.get(pk=form.cleaned_data["assignation"])
                except User.DoesNotExist:
                    return self.render_json({"messages":["user does not exists"]}, ok=False)

                task.assigned_to = person
                task.save()

        if "status" in form.cleaned_data and form.cleaned_data["status"]:
            task.status = form.cleaned_data["status"]
            task.save()

        return self.render_json({"task": task.to_dict()})
