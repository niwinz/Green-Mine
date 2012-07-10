# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.utils.timezone import now
from django.conf import settings

from ...profile.models import Role
from ...core.generic import GenericView
from ...core.decorators import login_required, staff_required
from ...core import signals

from ..models import Project
from ..forms.project import ProjectForm, ProjectPersonalSettingsForm, ProjectAdminSettingsForm

from greenmine.forms.base import *
from greenmine.questions.forms import *
from greenmine.scrum.forms.project import *
from greenmine.scrum.forms.milestone import *
from greenmine.core.utils import iter_points
from greenmine.core import signals
from greenmine.profile.models import *

from datetime import timedelta

import os
import re


class UserRoleMixIn(object):
    user_rx = re.compile(r'^user_(?P<userid>\d+)$', flags=re.U)

    def parse_roles(self):
        user_role = {}

        for post_key in self.request.POST.keys():
            user_rx_pos = self.user_rx.match(post_key)
            if not user_rx_pos:
                continue

            user_role[user_rx_pos.group('userid')] = self.request.POST[post_key]

        invalid_role = False
        for role in user_role.values():
            try:
                Role.objects.get(pk=role)
            except Role.DoesNotExist:
                invalid_role = True
                break

        return {} if invalid_role else user_role


class ProjectCreateView(UserRoleMixIn, GenericView):
    template_name = 'project-create.html'
    menu = ['projects']

    @login_required
    def get(self, request):
        form = ProjectForm()
        context = {'form':form, 'roles': Role.objects.all()}
        return self.render_to_response(self.template_name, context)

    @login_required
    def post(self, request):
        form = ProjectForm(request.POST)

        context = {
            'form': form,
            'roles': Role.objects.all(),
        }

        if not form.is_valid():
            response = {'errors': form.errors}
            return self.render_to_error(response)

        sem = transaction.savepoint()
        try:
            user_role = self.parse_roles()
            if not user_role:
                transaction.savepoint_rollback(sem)
                emsg = _(u'You must specify at least one person to the project')
                return self.render_to_error({
                    'messages': {'type': 'error', 'msg': emsg}
                })

            project = form.save(commit=False)
            project.owner = request.user
            project.save()

            for userid, role in user_role.iteritems():
                ProjectUserRole.objects.create(
                    project = project,
                    user = User.objects.get(pk=userid),
                    role = Role.objects.get(pk=role),
                )

        except Exception as e:
            transaction.savepoint_rollback(sem)
            return self.render_to_error({'messages': {'type':'error', 'msg': unicode(e)}})

        signals.mail_project_created.send(sender=self, project=project, user=request.user)

        transaction.savepoint_commit(sem)
        messages.info(request, _(u'Project %(pname)s is successful saved.') % {'pname':project.name})
        return self.render_to_ok({'redirect_to':reverse('projects')})

    @login_required
    def dispatch(self, *args, **kwargs):
        return super(ProjectCreateView, self).dispatch(*args, **kwargs)


class ProjectEditView(UserRoleMixIn, GenericView):
    template_name = 'config/project-edit.html'
    menu = ["settings", "editproject"]

    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(Project, slug=pslug)

        if not self.check_role(request.user, project, [('project',('view', 'edit'))], exception=None):
            return self.redirect_referer(_(u"You are not authorized to access here!"))

        form = ProjectForm(instance=project)

        context = {
            'form':form,
            'roles': Role.objects.all(),
            'project': project
        }
        return self.render_to_response(self.template_name, context)

    @login_required
    def post(self, request, pslug):
        project = get_object_or_404(Project, slug=pslug)

        if not self.check_role(request.user, project, [('project', ('view','edit'))], exception=None):
            return self.redirect_referer(_(u"You are not authorized to access here!"))

        form = ProjectForm(request.POST, instance=project)

        context = {
            'form': form,
            'roles': Role.objects.all(),
            'project': project,
        }

        if not form.is_valid():
            response = {'errors': form.errors}
            return self.render_to_error(response)

        sem = transaction.savepoint()

        try:
            user_role = self.parse_roles()
            if not user_role:
                transaction.savepoint_rollback(sem)
                emsg = _(u'You must specify at least one person to the project')
                return self.render_to_error({
                    'messages': {'type': 'error', 'msg': emsg}
                })

            project = form.save()
            ProjectUserRole.objects.filter(project=project).delete()

            for userid, role in user_role.iteritems():
                ProjectUserRole.objects.create(
                    project = project,
                    user = User.objects.get(pk=userid),
                    role = Role.objects.get(pk=role)
                )

        except Exception as e:
            transaction.savepoint_rollback(sem)
            return self.render_to_error({'messages': {'type':'error', 'msg': unicode(e)}})

        signals.mail_project_modified.send(sender=self, project=project, user=request.user)

        transaction.savepoint_commit(sem)
        messages.info(request, _(u'Project %(pname)s is successful saved.') % {'pname':project.name})
        return self.render_to_ok({'redirect_to':reverse('projects')})


class ProjectDelete(GenericView):
    @login_required
    @transaction.commit_on_success
    def post(self, request, pslug):
        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', ('view', 'edit', 'delete')),
        ])

        signals.mail_project_deleted\
            .send(sender=self, project=project, user=request.user)

        project.delete()
        return self.render_json({}, ok=True)




class ProjectUserSettings(GenericView):
    template_path = "config/project-personal.html"

    def get(self, request):
        return HttpResponse("TODO")


class ProjectUserSettingsIndividual(GenericView):
    def get(self, request, pslug):
        project = get_object_or_404(Project, slug=pslug)
        try:
            pur = get_object_or_404(project.user_roles, user=request.user)
        except Http404 as e:
            if request.user.is_superuser:
                return self.render_redirect(reverse("project-general-settings", args=[project.slug]))
            else:
                raise

        form = ProjectPersonalSettingsForm(instance=pur)

        context = {
            'pur': pur,
            'project': project,
            'form': form,
        }

        return HttpResponse("TODO")



class ProjectAdminSettings(GenericView):
    """
    Future project administration page.
    Only visible for owner and superuser.
    """
    template_path = "config/project-general.html"
    menu = ["settings", "settings_general"]

    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(Project, slug=pslug)
        extras = project.get_extras()

        self.check_role(request.user, project, [
            ('project', ('view', 'edit')),
        ])

        initial = {
            'markup': project.markup,
            'sprints': extras.sprints,
            'show_burndown': extras.show_burndown,
            'show_burnup': extras.show_burnup,
            'show_sprint_burndown': extras.show_sprint_burndown,
            'total_story_points': extras.total_story_points,
        }

        form = ProjectAdminSettingsForm(initial=initial)

        context = {
            'categorys': self.create_category_choices(project),
            'project': project,
            'form': form,
        }

        return self.render_to_response(self.template_path, context)

    @transaction.commit_on_success
    def save_form(self, project, form):
        project.markup = form.cleaned_data['markup']
        project.save()

        extras = project.get_extras()
        extras.sprints = form.cleaned_data['sprints']
        extras.show_burndown = form.cleaned_data['show_burndown']
        extras.show_sprint_burndown = form.cleaned_data['show_sprint_burndown']
        extras.show_burnup = form.cleaned_data['show_burnup']
        extras.total_story_points = form.cleaned_data['total_story_points']
        extras.save()

    @login_required
    def post(self, request, pslug):
        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', ('view', 'edit')),
        ])

        form = ProjectGeneralSettingsForm(request.POST)

        if form.is_valid():
            self.save_form(project, form)

            messages.info(request, _(u"Project preferences saved successfull"))
            return self.render_redirect(project.get_general_settings_url())


        context = {
            'categorys': self.create_category_choices(project),
            'project': project,
            'form': form,
        }

        return self.render_to_response(self.template_path, context)
