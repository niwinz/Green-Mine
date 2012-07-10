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

from ..models import *


class BacklogStats(GenericView):
    def calculate_stats(self, unassigned, assigned, completed):
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
            'percentage_completed': "{0:.2f}".format(percentage_completed),
            'percentage_assigned': "{0:.2f}".format(percentage_assigned),
        }

    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', 'view'),
        ])

        unassigned = project.user_stories\
            .filter(milestone__isnull=True)\
            .only('points')

        assigned = project.user_stories\
            .filter(milestone__isnull=False)\
            .only('points')

        completed = assigned.filter(status__in=['completed', 'closed'])

        context = self.calculate_stats(unassigned, assigned, completed)
        stats = loader.render_to_string("modules/backlog-stats.html", context)
        return self.render_to_ok({'stats_html': stats, 'stats': context})


class BacklogLeftBlockView(GenericView):
    """
    Get unassigned user story html part for backlog.
    API
    """

    template_path = 'backlog-left-block.html'

    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', 'view'),
        ])

        unassigned = project.user_stories\
            .filter(milestone__isnull=True)\
            .order_by('-priority')

        if "order_by" in request.GET:
            unassigned = unassigned.order_by(request.GET['order_by'])

        selected_tags = Tag.objects.none()
        if "tags" in request.GET and request.GET['tags']:
            selected_tags_ids = map(int, request.GET['tags'].split(','))
            selected_tags = Tag.objects.filter(id__in = selected_tags_ids)
            for tag in selected_tags:
                unassigned = unassigned.filter(tags__in=[tag])

        unassigned = unassigned.select_related()

        template_context = {
            'project': project,
            'unassigned_us': unassigned,
            'tags': Tag.objects.tags_for_queryset(unassigned),
            'selected_tags_ids': selected_tags.values_list('id', flat=True),
        }

        response_context = {
            'html': loader.render_to_string(self.template_path, template_context)
        }

        return self.render_to_ok(response_context)


class BacklogRightBlockView(GenericView):
    """
    Get milestones html part for backlog.
    API
    """

    template_path = 'backlog-right-block.html'

    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', 'view'),
        ])

        template_context = {
            'project': project,
            'milestones': project.milestones.order_by('-created_date')\
                .prefetch_related('project'),
        }

        response_context = {
            'html': loader.render_to_string(self.template_path, template_context),
        }

        return self.render_to_ok(response_context)


class BacklogBurnDownView(GenericView):
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

        context = {
            'points_for_sprint': points_for_sprint,
            'disponibility': disponibility,
            'sprints_number': extras.sprints,
            'extra_points': extra_points,
            #old
            #'total_points': sum(iter_points(project.user_stories.all())),
            'total_points': sum(iter_points(project.user_stories\
                .exclude(Q(client_requirement=True) | Q(team_requirement=True)))),
        }

        return self.render_to_ok(context)


class BacklogBurnUpView(GenericView):
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
        }

        return self.render_to_ok(context)


class BacklogView(GenericView):
    """
    General dasboard view,  with all milestones and all tasks.
    """

    template_name = 'backlog.html'
    menu = ['backlog']

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

        return self.render_to_response(self.template_name, context)
