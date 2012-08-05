# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django.template import loader
from django.db.models import Q

from greenmine.core.generic import GenericView
from greenmine.core.decorators import login_required

from datetime import timedelta
from greenmine.forms import base as forms
from greenmine.core.utils import iter_points
from greenmine.taggit.models import Tag

from django.utils import timezone

from ..models import *

class BacklogView(GenericView):
    """
    General dasboard view,  with all milestones and all tasks.
    """

    template_name = 'backlog.html'
    menu = ['backlog']

    def initialize_unassigned(self, project):
        unassigned = project.user_stories\
            .filter(milestone__isnull=True)\
            .order_by('-priority')

        if "order_by" in self.request.GET:
            unassigned = unassigned.order_by(self.request.GET['order_by'])

        selected_tags_ids = []

        if "tags" in self.request.GET and self.request.GET['tags']:
            selected_tags_ids = map(int, self.request.GET['tags'].split(','))

        if selected_tags_ids:
            unassigned = unassigned.filter(tags__pk__in=selected_tags_ids).distinct()

        context = {
            'unassigned_us': [x.to_dict() for x in unassigned],
            'tags': [x.to_dict() for x in Tag.objects.tags_for_queryset(unassigned)],
            'selected_tags_ids': selected_tags_ids,
        }
        return context

    def initialize_milestones(self, project):
        context = {
            'milestones': [x.to_dict() for x in project\
                .milestones.order_by('-created_date')\
                .prefetch_related('project')],
        }
        return context

    def initialize_stats(self, project):
        unassigned = project.user_stories\
            .filter(milestone__isnull=True)\
            .only('points')

        assigned = project.user_stories\
            .filter(milestone__isnull=False)\
            .only('points')

        completed = assigned.filter(status__in=['completed', 'closed'])

        unassigned_points = sum(iter_points(unassigned))
        assigned_points = sum(iter_points(assigned))
        completed_points = sum(iter_points(completed))

        total_points = unassigned_points + assigned_points

        try:
            percentage_assigned = (assigned_points * 100) / total_points
        except ZeroDivisionError:
            percentage_assigned = 0

        try:
            percentage_completed = (completed_points * 100) / total_points
        except ZeroDivisionError:
            percentage_completed = 0

        return {
            'unassigned_points': unassigned_points,
            'assigned_points': assigned_points,
            'total_points': total_points,
            'percentage_completed': "{0:.0f}".format(percentage_completed),
            'percentage_assigned': "{0:.0f}".format(percentage_assigned),
            'completed_points': completed_points,
        }

    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', 'view'),
        ])

        context = {
            'project': project,
            'project_extras': project.get_extras()
        }

        context.update(self.initialize_unassigned(project))
        context.update(self.initialize_milestones(project))
        context.update({'stats': self.initialize_stats(project)})
        return self.render_to_response(self.template_name, context)


class BacklogUnassignedUsApi(BacklogView):
    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', 'view'),
        ])

        context = self.initialize_unassigned(project)
        return self.render_json(context, ok=True)


class BacklogMilestonesApi(BacklogView):
    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', 'view'),
        ])

        context = self.initialize_milestones(project)
        return self.render_json(context, ok=True)


class BacklogStatsApi(BacklogView):
    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', 'view'),
        ])

        context = self.initialize_stats(project)
        return self.render_json(context)


class BacklogBurndownApi(GenericView):
    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', 'view'),
        ])

        extras = project.get_extras()

        points_sum, extra_points_sum = 0, 0
        points_for_sprint = [points_sum]
        disponibility, extra_points = [], [0]

        sprints_queryset = project.milestones.order_by('created_date')

        now_position = None

        for i, sprint in enumerate(sprints_queryset, 1):
            usqs = sprint.user_stories.filter(status__in=['completed', 'closed'])
            points_sum += sum(iter_points(usqs))

            extra_points_user_stories = UserStory.objects.filter(
                created_date__gte=sprint.created_date,
                created_date__lte=sprint.estimated_finish
            )

            extra_points_user_stories_shareds = extra_points_user_stories\
                .filter(client_requirement=True, team_requirement=True)
            extra_points_sum += sum(x/2.0 for x in iter_points(extra_points_user_stories_shareds))


            extra_points_user_stories = extra_points_user_stories\
                .filter(client_requirement=True, team_requirement=False)
            extra_points_sum += sum(iter_points(extra_points_user_stories))
            extra_points.append(extra_points_sum)

            points_for_sprint.append(points_sum)
            disponibility.append(sprint.disponibility)

            if timezone.now().date() <= sprint.estimated_finish and timezone.now().date() >= sprint.estimated_start:
                end_days = (sprint.estimated_finish-sprint.estimated_start).days
                now_days = (timezone.now().date()-sprint.estimated_start).days
                now_position = (float(now_days)/float(end_days))+i

        context = {
            'points_for_sprint': points_for_sprint,
            'disponibility': disponibility,
            'sprints_number': extras.sprints,
            'extra_points': extra_points,
            'now_position': now_position,
            #old
            #'total_points': sum(iter_points(project.user_stories.all())),
            'total_points': sum(iter_points(project.user_stories\
                .exclude(Q(client_requirement=True) | Q(team_requirement=True)))),
        }

        return self.render_to_ok(context)


class BacklogBurnupApi(GenericView):
    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', 'view'),
        ])

        extras = project.get_extras()

        points_sum = 0
        points_for_sprint = [points_sum]
        disponibility = []
        extra_points = [0]
        extra_points_sum = 0
        extra_points_team = [0]
        extra_points_team_sum = 0

        sprints_queryset = project.milestones.order_by('created_date')

        now_position = None

        for i, sprint in enumerate(sprints_queryset, 1):
            usqs = sprint.user_stories.filter(status__in=['completed', 'closed'])
            points_sum += sum(iter_points(usqs))

            extra_points_user_stories = UserStory.objects.filter(
                created_date__gt=sprint.created_date,
                created_date__lt=sprint.estimated_finish
            )

            extra_points_user_stories_shareds = extra_points_user_stories\
                .filter(client_requirement=True, team_requirement=True)
            extra_points_sum += sum(x/2.0 for x in iter_points(extra_points_user_stories_shareds))

            extra_points_user_stories = extra_points_user_stories\
                .filter(client_requirement=True, team_requirement=False)
            extra_points_sum += sum(iter_points(extra_points_user_stories))
            extra_points.append(extra_points_sum)

            extra_points_team_user_stories = UserStory.objects.filter(
                created_date__gt=sprint.created_date,
                created_date__lt=sprint.estimated_finish
            )

            extra_points_team_user_stories_shareds = extra_points_team_user_stories\
                .filter(team_requirement=True, client_requirement=True)

            extra_points_team_sum += sum(x/2.0 for x in iter_points(extra_points_team_user_stories_shareds))

            extra_points_team_user_stories = extra_points_team_user_stories\
                .filter(team_requirement=True, client_requirement=False)

            extra_points_team_sum += sum(iter_points(extra_points_team_user_stories))
            extra_points_team.append(extra_points_team_sum)

            points_for_sprint.append(points_sum)

            if timezone.now().date() <= sprint.estimated_finish and timezone.now().date() >= sprint.estimated_start:
                end_days = (sprint.estimated_finish-sprint.estimated_start).days
                now_days = (timezone.now().date()-sprint.estimated_start).days
                now_position = (float(now_days)/float(end_days))+i

        total_points = sum(iter_points(project.user_stories.all()))

        sprints = []
        sprints.append(points_for_sprint)
        sprints.append(extra_points_team)
        sprints.append(extra_points)

        context = {
            'sprints': sprints,
            #'total_points': sum(iter_points(project.user_stories.all())),
            'total_points': sum(iter_points(project.user_stories\
                .exclude(Q(client_requirement=True) | Q(team_requirement=True)))),
            'total_sprints': extras.sprints,
            'now_position': now_position,
        }

        return self.render_to_ok(context)



