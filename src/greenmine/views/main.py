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

from django.utils.encoding import force_unicode
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.cache import cache_page

from greenmine.views.generic import GenericView
from greenmine.views.decorators import login_required, staff_required
from greenmine import models, forms
from greenmine.utils import iter_points
from greenmine import permissions as perms, signals

from greenmine.middleware import PermissionDeniedException
from greenqueue import send_task

import os
import re

class RegisterView(GenericView):
    template_path = 'register.html'

    def get(self, request):
        if settings.DISABLE_REGISTRATION:
            messages.warning(request, _(u"Registration system is disabled."))

        form = forms.RegisterForm()
        context = {'form':form}
        return self.render_to_response(self.template_path, context)

    def post(self, request):
        if settings.DISABLE_REGISTRATION:
            return self.render_redirect(reverse('web:register'))

        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            user = User(
                username = form.cleaned_data['username'],
                first_name = form.cleaned_data['first_name'],
                last_name = form.cleaned_data['last_name'],
                email = form.cleaned_data['email'],
                is_active = False,
                is_staff = False,
                is_superuser = False,
            )
            
            user.set_password(form.cleaned_data['password'])
            user.save()

            signals.mail_new_user.send(sender=self, user=user)
            messages.info(request, _(u"Validation message was sent successfully."))

            return self.render_redirect(reverse('web:login'))

        context = {'form': form}
        return self.render_to_response(self.template_path, context)


class AccountActivation(GenericView):
    def get(self, request, token):
        try:
            profile = models.Profile.objects.get(token=token)
            profile.user.is_active = True
            profile.token = None

            profile.user.save()
            profile.save()

            messages.info(request, _(u"User %(username)s is now activated!") % \
                {'username': profile.user.username})

        except models.Profile.DoesNotExist:
            messages.error(request, _(u"Invalid token"))

        return self.render_redirect(reverse("web:login"))


class LoginView(GenericView):
    template_name = 'login.html'
    
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        login_form = forms.LoginForm(request=request)

        context = {
            'form': login_form,
            'register_disabled': settings.DISABLE_REGISTRATION,
        }

        return self.render_to_response(self.template_name, context)

    def post(self, request):
        login_form = forms.LoginForm(request.POST, request=request)
        if request.is_ajax():
            if login_form.is_valid():
                user_profile = login_form._user.get_profile()
                if user_profile.default_language:
                    request.session['django_language'] = user_profile.default_language

                return self.render_to_ok({'redirect_to':'/'})
            
            return self.render_json_error(login_form.errors)
        return self.render_json({'error_msg':'Invalid request'}, ok=False)


class RememberPasswordView(GenericView):
    """
    Remember password procedure for non logged users.
    This sends the password revery mail with link for
    a recovery procedure.
    """

    template_name = 'remember-password.html'
    
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        form = forms.ForgottenPasswordForm()

        return self.render_to_response(self.template_name, 
            {'form': form})
    
    def post(self, request):
        form = forms.ForgottenPasswordForm(request.POST)
        if form.is_valid():
            form.user.set_unusable_password()
            form.user.save()
            
            signals.mail_recovery_password.send(sender=self, user=form.user)
            messages.info(request, _(u'He has sent an email with the link to retrieve your password'))

            return self.render_to_ok({'redirect_to':'/'})

        response = {'errors': form.errors}
        return self.render_to_error(response)


class SendRecoveryPasswordView(GenericView):
    """
    Staff's method for send recovery password.
    """

    @login_required
    @staff_required
    def get(self, request, uid):
        user = get_object_or_404(User.objects.select_for_update(), pk=uid)
        user.set_unusable_password()
        user.save()
        
        signals.mail_recovery_password.send(sender=self, user=user)
        messages.info(request, _(u"Recovery password email are sended"))

        referer = request.META.get('HTTP_REFERER', reverse('web:users-edit', args=[uid]))
        return self.render_redirect(referer)


class PasswordChangeView(GenericView):
    """
    User profile - password change view.
    """

    template_path = 'password.html'

    @login_required    
    def get(self, request):
        form = forms.PasswordRecoveryForm()
        context = {'form': form}
        return self.render_to_response(self.template_path, context)

    @login_required
    def post(self, request):
        form = forms.PasswordRecoveryForm(request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['password'])
            request.user.save()
            messages.info(request, _(u"Password changed!"))
            return self.render_redirect(reverse('web:profile'))

        context = {'form': form}
        return self.render_to_response(self.template_path, context)


class PasswordRecoveryView(GenericView):
    """
    Simple recovery password procedure.
    """

    template_name = "password_recovery.html"

    def get(self, request, token):
        form = forms.PasswordRecoveryForm()
        context = {'form':form}
        return self.render_to_response(self.template_name, context)

    def post(self, request, token):
        form = forms.PasswordRecoveryForm(request.POST)
        if form.is_valid():
            profile_queryset = models.Profile.objects.filter(token=token)
            if not profile_queryset:
                messages.error(request, _(u'Token has expired, try again'))
                return self.render_redirect(reverse('web:login'))

            profile = profile_queryset.get()
            user = profile.user
            user.set_password(form.cleaned_data['password'])
            user.save()

            profile.token = None
            profile.save()

            messages.info(request, _(u'The password has been successfully restored.'))
            return self.render_redirect(reverse('web:login'))

        context = {'form':form}
        return self.render_to_response(self.template_name, context)


class ProfileView(GenericView):
    template_name = 'profile.html'

    @login_required
    def get(self, request):
        form = forms.ProfileForm(instance=request.user)
        context = {'form':form}
        return self.render_to_response(self.template_name, context)

    @login_required
    def post(self, request):
        form = forms.ProfileForm(request.POST, request.FILES, instance=request.user)
        context = {'form':form}

        if not form.is_valid():
            return self.render_to_response(self.template_name, context)

        sem = transaction.savepoint()
        try:
            request.user = form.save()
        except IntegrityError as e:
            transaction.savepoint_rollback(sem)
            
            messages.error(request, _(u'Integrity error: %(e)s') % {'e':unicode(e)})
            return self.render_to_response(self.template_name, context)
        
        transaction.savepoint_commit(sem)
        messages.info(request, _(u'Profile save success!'))
        return HttpResponseRedirect(reverse('web:profile'))


class HomeView(GenericView):
    """
    General user projects view. This is a home page.
    """

    template_name = 'projects.html'
    menu = ['projects']

    @login_required
    def get(self, request, *args, **kwargs):
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
        
        if request.user.is_staff:
            projects = models.Project.objects.all()
        else:
            projects = request.user.projects.all() | \
                request.user.projects_participant.all()
        
        projects = projects.order_by('name').distinct()
        paginator = Paginator(projects, 20)
        page = paginator.page(page)

        context = {
            'is_paginated': True if paginator.count else False,
            'page': page,
            'projects': projects,
        }
        return self.render_to_response(self.template_name, context)


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
        project = get_object_or_404(models.Project, slug=pslug)

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

        unassigned = unassigned.select_related()
        template_context = {
            'project': project,
            'unassigned_us': unassigned,
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
        project = get_object_or_404(models.Project, slug=pslug)

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
        project = get_object_or_404(models.Project, slug=pslug)

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

            extra_points_user_stories = models.UserStory.objects.filter(
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
        project = get_object_or_404(models.Project, slug=pslug)

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

            extra_points_user_stories = models.UserStory.objects.filter(
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

            extra_points_team_user_stories = models.UserStory.objects.filter(
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
        project = get_object_or_404(models.Project, slug=pslug)

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


class TasksView(GenericView):
    """
    Tasks/Bugs view.
    """

    template_name = 'tasks.html'
    menu = ['tasks']

    @login_required
    def get(self, request, pslug, mid=None, filter_by=None):
        project = get_object_or_404(models.Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', 'view'),
            ('task', 'view'),
        ])
        
        if mid is None:
            try:
                return self.render_redirect(project.get_default_tasks_url())
            except IndexError:
                messages.error(request, _("No milestones found"))
                return self.render_redirect(project.get_backlog_url())

        milestone = get_object_or_404(project.milestones, pk=mid)
        tasks = milestone.tasks.all()

        if filter_by is not None:
            if filter_by == "task":
                tasks = tasks.filter(type="task")
            elif filter_by == 'bug':
                tasks = tasks.filter(type="bug")

        if "order_by" in request.GET:
            tasks = tasks.order_by(request.GET['order_by'])

        context = {
            'project': project,
            'milestones': project.milestones.order_by('-created_date'),
            'milestone': milestone,
            'tasks': tasks,
        }

        return self.render_to_response(self.template_name, context)


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
            'user_stories':milestone.user_stories.order_by('subject'),
            'milestones': milestones,
            'milestone':milestone,
            'project': project,
            'status_list': models.TASK_STATUS_CHOICES,
            'participants': project.all_participants,
            'form': form,
        }
        return self.render_to_response(self.template_name, context)


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
                models.Role.objects.get(pk=role)
            except models.Role.DoesNotExist:
                invalid_role = True
                break
            
        return {} if invalid_role else user_role


class ProjectCreateView(UserRoleMixIn, GenericView):
    template_name = 'project-create.html'
    menu = ['projects']
    
    @login_required
    def get(self, request):
        form = forms.ProjectForm()
        context = {'form':form, 'roles': models.Role.objects.all()}
        return self.render_to_response(self.template_name, context)
    
    @login_required
    def post(self, request):
        form = forms.ProjectForm(request.POST)
        
        context = {
            'form': form, 
            'roles': models.Role.objects.all(),
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
                models.ProjectUserRole.objects.create(
                    project = project,
                    user = models.User.objects.get(pk=userid),
                    role = models.Role.objects.get(pk=role),
                )

        except Exception as e:
            transaction.savepoint_rollback(sem)
            return self.render_to_error({'messages': {'type':'error', 'msg': unicode(e)}})
        
        signals.mail_project_created.send(sender=self, project=project, user=request.user)

        transaction.savepoint_commit(sem)
        messages.info(request, _(u'Project %(pname)s is successful saved.') % {'pname':project.name})
        return self.render_to_ok({'redirect_to':reverse('web:projects')})

    @login_required
    def dispatch(self, *args, **kwargs):
        return super(ProjectCreateView, self).dispatch(*args, **kwargs)


class ProjectEditView(UserRoleMixIn, GenericView):
    template_name = 'config/project-edit.html'
    menu = ["settings", "editproject"]

    @login_required
    def get(self, request, pslug):		
        project = get_object_or_404(models.Project, slug=pslug)

        if not self.check_role(request.user, project, [('project',('view', 'edit'))], exception=None):
            return self.redirect_referer(_(u"You are not authorized to access here!"))

        form = forms.ProjectForm(instance=project)
        
        context = {
            'form':form, 
            'roles': models.Role.objects.all(),
            'project': project
        }
        return self.render_to_response(self.template_name, context)

    @login_required
    def post(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)

        if not self.check_role(request.user, project, [('project', ('view','edit'))], exception=None):
            return self.redirect_referer(_(u"You are not authorized to access here!"))
        
        form = forms.ProjectForm(request.POST, instance=project)
        
        context = {
            'form': form, 
            'roles': models.Role.objects.all(),
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
            models.ProjectUserRole.objects.filter(project=project).delete()

            for userid, role in user_role.iteritems():
                models.ProjectUserRole.objects.create(
                    project = project,
                    user = User.objects.get(pk=userid),
                    role = models.Role.objects.get(pk=role)
                )

        except Exception as e:
            transaction.savepoint_rollback(sem)
            return self.render_to_error({'messages': {'type':'error', 'msg': unicode(e)}})
        
        signals.mail_project_modified.send(sender=self, project=project, user=request.user)

        transaction.savepoint_commit(sem)
        messages.info(request, _(u'Project %(pname)s is successful saved.') % {'pname':project.name})
        return self.render_to_ok({'redirect_to':reverse('web:projects')})  


class ProjectDelete(GenericView):
    @login_required
    def post(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', ('view', 'edit', 'delete')),
        ])
        
        signals.mail_project_deleted\
            .send(sender=self, project=project, user=request.user)

        project.delete()

        return self.render_to_ok({})


class MilestoneCreateView(GenericView):
    template_name = 'milestone-create.html'
    menu = []

    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', ('view', 'edit', 'create')),
        ])

        form = forms.MilestoneForm(initial={'estimated_start': now()})
        context = {
            'form': form,
            'project': project,
        }

        return self.render_to_response(self.template_name, context)

    @login_required
    def post(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', ('view', 'create')),
        ])
        
        form = forms.MilestoneForm(request.POST)

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
        project = get_object_or_404(models.Project, slug=pslug)
        milestone = get_object_or_404(project.milestones, pk=mid)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', ('view', 'edit', 'create')),
        ])

        form = forms.MilestoneForm(instance=milestone)

        context = {
            'form': form,
            'project': project,
        }

        return self.render_to_response(self.template_name, context)

    @login_required
    def post(self, request, pslug, mid):
        project = get_object_or_404(models.Project, slug=pslug)
        milestone = get_object_or_404(project.milestones, pk=mid)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', ('view', 'create')),
        ])
        
        form = forms.MilestoneForm(request.POST, instance=milestone)

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
        project = get_object_or_404(models.Project, slug=pslug)
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
        

class UserStoryView(GenericView):
    template_name = "user-story-view.html"

    @login_required
    def get(self, request, pslug, iref):
        """ View US Detail """
        project = get_object_or_404(models.Project, slug=pslug)
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
        project = get_object_or_404(models.Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', ('view', 'edit')),
            ('userstory', ('view', 'create')),
        ])

        if mid is not None:
            milestone = get_object_or_404(project.milestones, pk=mid)
        else:
            milestone = None
        
        form = forms.UserStoryForm(initial={'milestone': milestone})
        context = {
            'form':form, 
            'project':project,
        }
        return self.render_to_response(self.template_name, context)

    @login_required
    def post(self, request, pslug, mid=None):
        project = get_object_or_404(models.Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', ('view', 'edit')),
            ('userstory', ('view', 'create')),
        ])

        if mid is not None:
            milestone = get_object_or_404(project.milestones, pk=mid)
        else:
            milestone = None

        form = forms.UserStoryForm(request.POST, initial={'milestone': milestone})

        if form.is_valid():
            instance = form.save(commit=False)
            instance.milestone = milestone
            instance.owner = request.user
            instance.project = project
            instance.save()

            signals.mail_userstory_created.send(sender=self, us=instance, user=request.user)
            self.create_asociated_tasks(project, instance)
            
            messages.info(request, _(u'The user story was created correctly'))
            return self.render_redirect(project.get_backlog_url())
    
        context = {
            'form':form, 
            'project':project,
        }
        return self.render_to_response(self.template_name, context)

    def create_asociated_tasks(self, project, user_story):
        texts = list(project.get_extras().parse_ustext(user_story.description))
        tasks = []

        for text in texts:
            task = models.Task(
                user_story=user_story, 
                ref = models.ref_uniquely(project, user_story.__class__),
                description = "",
                project = project,
                milestone = user_story.milestone,
                owner = self.request.user,
                subject = text
            )
            tasks.append(task)

        models.Task.objects.bulk_create(tasks)

        for task in tasks:
            signals.mail_task_created.send(sender=self,
                task = task, user = self.request.user)
        

class UserStoryEdit(GenericView):
    template_name = "user-story-edit.html"

    @login_required
    def get(self, request, pslug, iref):
        project = get_object_or_404(models.Project, slug=pslug)
        user_story = get_object_or_404(project.user_stories, ref=iref)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', ('view', 'edit')),
            ('userstory', ('view', 'edit')),
        ])

        form = forms.UserStoryForm(instance=user_story)
        context = {
            'project': project,
            'user_story': user_story,
            'form': form,
        }
        return self.render_to_response(self.template_name, context)

    @login_required
    def post(self, request, pslug, iref):
        project = get_object_or_404(models.Project, slug=pslug)
        user_story = get_object_or_404(project.user_stories, ref=iref)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', ('view', 'edit')),
            ('userstory', ('view', 'edit')),
        ])

        form = forms.UserStoryForm(request.POST, instance=user_story)
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
        project = get_object_or_404(models.Project, slug=pslug)
        user_story = get_object_or_404(project.user_stories, ref=iref)
        
        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', ('view', 'edit')),
            ('userstory', ('view', 'edit', 'delete')),
        ])

        signals.mail_userstory_deleted.send(sender=self, us=user_story, user=request.user)
        user_story.delete()

        return self.render_to_ok()


class TaskCreateView(GenericView):
    template_name = 'task-create.html'

    menu = ["tasks"]

    @login_required
    def get(self, request, pslug, usref=None, mid=None):
        project = get_object_or_404(models.Project, slug=pslug)

        if usref is not None and mid is not None:
            return HttpResponseBadRequest()

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', 'view'),
            ('task', ('view', 'create')),
        ])
        
        if usref is not None:
            user_story = get_object_or_404(project.user_stories, ref=usref)
            milestone = user_story.milestone
        elif mid is not None:
            user_story = None
            milestone = get_object_or_404(project.milestones, pk=mid)
        else:
            return HttpResponseBadRequest()

        form = forms.TaskForm(project=project, 
            initial={'milestone':milestone, 'user_story': user_story})

        context = {
            'project': project,
            'form': form,
        }
        return self.render_to_response(self.template_name, context)

    @login_required
    def post(self, request, pslug, usref=None, mid=None):
        project = get_object_or_404(models.Project, slug=pslug)

        if usref is None and mid is None:
            return HttpResponseBadRequest()

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', 'view'),
            ('task', ('view', 'create')),
        ])

        if usref is not None:
            user_story = get_object_or_404(project.user_stories, ref=usref)
            milestone = user_story.milestone
        elif mid is not None:
            user_story = None
            milestone = get_object_or_404(project.milestones, pk=mid)
        else:
            return HttpResponseBadRequest()

        form = forms.TaskForm(request.POST, project=project,
            initial={'milestone':milestone, 'user_story': user_story})

        next_url = request.GET.get('next', None)
        _from = request.POST.get('from', '')

        if form.is_valid():
            task = form.save(commit=False)
            task.owner = request.user
            task.project = project
            task.save()

            signals.mail_task_created.send(sender=self, task=task, user=request.user)

            if task.assigned_to != None:
                signals.mail_task_assigned.send(sender=self, task=task, user=request.user)
    
            if _from == 'dashboard':
                return self.create_response_for_dashboard(form, task, project)
            
            messages.info(request, _(u"The task has been created with success!"))
            response = {}

            if next_url:
                response['redirect_to'] = next_url
            else:
                response['redirect_to'] = task.milestone.get_tasks_url()

            return self.render_json(response)

        return self.render_json_error(form.errors)

    def create_response_for_dashboard(self, form, task, project):
        html = loader.render_to_string("dashboard-userstory-task.html", {
            'task':task, 
            'project': project, 
            'participants': project.all_participants,
            'status_list': models.TASK_STATUS_CHOICES,
        })

        response = {
            'html': html,
            'status': task.status,
            'userStory': task.user_story.id if task.user_story else None,
        }

        return self.render_json(response)
        

class TaskView(GenericView):
    menu = ['tasks']
    template_path = 'task-view.html'

    @login_required
    def get(self, request, pslug, tref):
        project = get_object_or_404(models.Project, slug=pslug)
        task = get_object_or_404(project.tasks, ref=tref)
        form = forms.CommentForm()
        
        context = {
            'form': form,
            'task': task,
            'project': project,
        }

        return self.render_to_response(self.template_path, context)
    
    @login_required
    def post(self, request, pslug, tref):
        """ 
        Add comments method.
        """

        project = get_object_or_404(models.Project, slug=pslug)
        task = get_object_or_404(project.tasks, ref=tref)
        form = forms.CommentForm(request.POST, request.FILES)
        
        if form.is_valid():
            self.create_task_comment(request.user, project, task, form.cleaned_data)
            return self.render_redirect(task.get_view_url())

        context = {
            'form': form,
            'task': task,
            'project': project,
        }
        return self.render_to_response(self.template_path, context)
    
    @transaction.commit_on_success
    def create_task_comment(self, owner, project, task, cleaned_data):
        change_instance = models.Change(
            change_type = models.TASK_COMMENT,
            owner = owner,
            content_object = task,
            project = project,
            data = {'comment': cleaned_data['description']},
        )

        change_instance.save()
        
        if "attached_file" in cleaned_data:
            change_attachment = models.ChangeAttachment(
                owner = owner,
                change = change_instance,
                attached_file = cleaned_data['attached_file']
            )
            change_attachment.save()
    

class TaskEdit(GenericView):
    template_path = 'task-edit.html'

    @login_required
    def get(self, request, pslug, tref):
        project = get_object_or_404(models.Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', 'view'),
            ('task', ('view', 'edit')),
        ])

        task = get_object_or_404(project.tasks, ref=tref)
        form = forms.TaskForm(instance=task, project=project)

        context = {
            'project': project,
            'task': task,
            'form': form,
        }

        return self.render_to_response(self.template_path, context)

    @login_required
    def post(self, request, pslug, tref):
        project = get_object_or_404(models.Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', 'view'),
            ('task', ('view', 'edit')),
        ])

        task = get_object_or_404(project.tasks.select_for_update(), ref=tref)
        form = forms.TaskForm(request.POST, instance=task, project=project)

        next_url = request.GET.get('next', None)

        _old_assigned_to_pk = task.assigned_to.pk if task.assigned_to else None

        if form.is_valid():
            task = form.save(commit=True)
            signals.mail_task_modified.send(sender=self, task=task, user=request.user)
            
            if task.assigned_to.pk != _old_assigned_to_pk:
                signals.mail_task_assigned.send(sender=self, task=task, user=request.user)

            messages.info(request, _(u"The task has been saved!"))
            if next_url:
                return self.render_redirect(next_url)

            return self.render_redirect(task.get_view_url())

        context = {
            'project': project,
            'task': task,
            'form': form,
        }
        
        return self.render_to_response(self.template_path, context)


class TaskDelete(GenericView):
    @login_required
    def post(self, request, pslug, tref):
        project = get_object_or_404(models.Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', 'view'),
            ('task', ('view', 'edit', 'delete')),
        ])
        
        task = get_object_or_404(project.tasks, ref=tref)
        signals.mail_task_deleted.send(sender=self, task=task, user=request.user)
        task.delete()
        
        return self.render_to_ok({})


class AssignUserStory(GenericView):
    """
    Assign user story callback.
    """

    template_name  = "milestone-item.html"

    @login_required
    def post(self, request, pslug, iref):
        if "mid" not in request.POST:
            return self.render_to_error()

        project = get_object_or_404(models.Project, slug=pslug)

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
        project = get_object_or_404(models.Project, slug=pslug)

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


class ProjectSettings(GenericView):
    template_path = "config/project-personal.html"
    menu = ['settings', 'settings_personal']

    def create_category_choices(self, project):
        return [('', '-----'),] + [(key, key.title()) \
            for key in project.meta_category_list]

    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        try:
            pur = get_object_or_404(project.user_roles, user=request.user)
        except Http404 as e:
            if request.user.is_superuser:
                return self.render_redirect(reverse("web:project-general-settings", args=[project.slug]))
            else:
                raise

        form = forms.ProjectPersonalSettingsForm(instance=pur)

        context = {
            'categorys': self.create_category_choices(project),
            'pur': pur,
            'project': project,
            'form': form,
        }

        return self.render_to_response(self.template_path, context)

    @login_required
    def post(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        pur = get_object_or_404(project.user_roles, user=request.user)
        form = forms.ProjectPersonalSettingsForm(request.POST, instance=pur)

        if form.is_valid():
            pur = form.save(commit=True)
            messages.info(request, _(u"Project preferences saved successfull"))

            return self.render_redirect(project.get_settings_url())

        context = {
            'pur': pur,
            'project': project,
            'form': form,
        }

        return self.render_to_response(self.template_path, context)


class ProjectGeneralSettings(GenericView):
    template_path = "config/project-general.html"
    menu = ["settings", "settings_general"]

    def create_category_choices(self, project):
        return [('', '-----'),] + [(key, key.title()) \
            for key in project.meta_category_list]

    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        extras = project.get_extras()

        self.check_role(request.user, project, [
            ('project', ('view', 'edit')),
        ])

        initial = {
            'markup': project.markup,
            'sprints': extras.sprints,
            'show_burndown': extras.show_burndown,
            'show_burnup': extras.show_burnup,
            'total_story_points': extras.total_story_points,
        }

        form = forms.ProjectGeneralSettingsForm(initial=initial)

        context = {
            'categorys': self.create_category_choices(project),
            'project': project,
            'form': form,
        }

        return self.render_to_response(self.template_path, context)
    
    @transaction.commit_on_success
    def save_form(self, project, form):
        project.meta_category_color = form.colors_data
        project.markup = form.cleaned_data['markup']
        project.save()

        extras = project.get_extras()
        extras.sprints = form.cleaned_data['sprints']
        extras.show_burndown = form.cleaned_data['show_burndown']
        extras.show_burnup = form.cleaned_data['show_burnup']
        extras.total_story_points = form.cleaned_data['total_story_points']
        extras.save()

    @login_required
    def post(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', ('view', 'edit')),
        ])

        form = forms.ProjectGeneralSettingsForm(request.POST)

        if form.is_valid():
            self.save_form(project, form)

            messages.info(request, _(u"Project preferences saved successfull"))
            return self.render_redirect(project.get_general_settings_url())
        

        print dict(form.errors)
        context = {
            'categorys': self.create_category_choices(project),
            'project': project,
            'form': form,
        }

        return self.render_to_response(self.template_path, context)


class Documents(GenericView):
    template_path = 'documents.html'
    menu = ['documents']

    # TODO: fix permissions

    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
        ])

        documents = project.documents.order_by('-created_date')

        context = {
            'documents': documents,
            'project': project,
            'form': forms.DocumentForm(),
        }

        return self.render_to_response(self.template_path, context)
    
    @login_required
    def post(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
        ])

        form = forms.DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = models.Document.objects.create(
                title = form.cleaned_data['title'],
                owner = request.user,
                project = project,
                attached_file = form.cleaned_data['document'],
            )

            html = loader.render_to_string("documents-item.html",
                {'doc': document})

            return self.render_to_ok({'html': html})

        return self.render_json_error(form.errors)


class DocumentsDelete(GenericView):
    @login_required
    def post(self, request, pslug, docid):
        project = get_object_or_404(models.Project, slug=pslug)
        document = get_object_or_404(project.documents, pk=docid)

        document.delete()
        return self.render_to_ok()


class QuestionsListView(GenericView):
    template_path = 'questions.html'
    menu = ['questions']

    def get(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        questions = project.questions.order_by('-created_date')

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('question', 'view'),
        ])

        context = {
            'open_questions': questions.filter(closed=False),
            'closed_questions': questions.filter(closed=True),
            'project': project,
        }

        return self.render_to_response(self.template_path, context)


class QuestionsCreateView(GenericView):
    template_path = 'questions-create.html'
    menu = ['questions']
    
    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        form = forms.QuestionCreateForm(project=project)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('question', ('view', 'create')),
        ])

        context = {
            'form': form,
            'project': project,
        }

        return self.render_to_response(self.template_path, context)

    @login_required
    def post(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        form = forms.QuestionCreateForm(request.POST, project=project)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('question', ('view', 'create')),
        ])

        if form.is_valid():
            question = form.save(commit=False)
            question.project = project
            question.owner = request.user
            question.save()

            signals.mail_question_created.send(sender=self, question=question)
            signals.mail_question_assigned.send(sender=self, question=question)

            messages.info(request, _(u"Question are created"))
            return self.render_redirect(question.get_view_url())

        context = {
            'form': form,
            'project': project,
        }
        return self.render_to_response(self.template_path, context)


class QuestionsEditView(GenericView):
    template_path = 'questions-edit.html'
    menu = ['questions']

    @login_required
    def get(self, request, pslug, qslug):
        project = get_object_or_404(models.Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('question', ('view', 'edit')),
        ])

        question = get_object_or_404(project.questions, slug=qslug)
        form = forms.QuestionCreateForm(instance=question, project=project)

        context = {
            'form': form,
            'project': project,
            'question': question,
        }
        return self.render_to_response(self.template_path, context)
    
    @login_required
    def post(self, request, pslug, qslug):
        project = get_object_or_404(models.Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('question', ('view', 'edit')),
        ])

        question = get_object_or_404(project.questions, slug=qslug)
        form = forms.QuestionCreateForm(request.POST, instance=question, project=project)

        _old_assigned_to_pk = question.assigned_to.pk

        if form.is_valid():
            question = form.save(commit=False)
            question.save()

            if question.assigned_to.pk != _old_assigned_to_pk:
                signals.mail_question_assigned.send(sender=self, question=question)

            messages.info(request, _(u"Quienstion are saved"))
            return self.render_redirect(question.get_view_url())

        context = {
            'form': form,
            'project': project,
            'question': question,
        }
        return self.render_to_response(self.template_path, context)


class QuestionsView(GenericView):
    template_path ='questions-view.html'
    menu = ['questions']

    @login_required
    def get(self, request, pslug, qslug):
        project = get_object_or_404(models.Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('question', 'view'),
        ])

        question = get_object_or_404(project.questions, slug=qslug)
        form = forms.QuestionResponseForm()
        
        context = {
            'form': form,
            'project': project,
            'question': question,
            'responses': question.responses.order_by('created_date'),
        }
        return self.render_to_response(self.template_path, context)

    @login_required
    def post(self, request, pslug, qslug):
        project = get_object_or_404(models.Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('question', 'view'),
        ])

        question = get_object_or_404(project.questions, slug=qslug)
        form = forms.QuestionResponseForm(request.POST)

        if form.is_valid():
            response = form.save(commit=False)
            response.owner = request.user
            response.question = question
            response.save()
            return self.render_redirect(question.get_view_url())

        context = {
            'form': form,
            'project': project,
            'question': question,
        }
        return self.render_to_response(self.template_path, context)


class QuestionsDeleteView(GenericView):
    template_path = 'questions-delete.html'

    def get_context(self):
        project = get_object_or_404(models.Project, slug=self.kwargs['pslug'])

        self.check_role(self.request.user, project, [
            ('project', 'view'),
            ('question', ('view', 'delete')),
        ])

        question = get_object_or_404(project.questions, slug=self.kwargs['qslug'])

        context = {
            'project': project,
            'question': question,
        }
        return context

    @login_required
    def get(self, request, **kwargs):
        context = self.get_context()
        return self.render_to_response(self.template_path, context)
    
    @login_required
    def post(self, request, **kwargs):
        context = self.get_context()
        context['question'].delete()
        return self.render_redirect(context['project'].get_questions_url())


class UserList(GenericView):
    template_path = 'config/users.html'
    menu = ['users']
    
    @login_required
    @staff_required
    def get(self, request):
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
        
        users = User.objects.all()
        paginator = Paginator(users, 20)
        page = paginator.page(page)

        context = {
            'is_paginated': True if paginator.count else False,
            'page': page,
            'users': users,
        }
        return self.render_to_response(self.template_path, context)


class UserView(GenericView):
    template_path = 'config/users-view.html'
    menu = ['users']

    @login_required
    @staff_required
    def get(self, request, uid):
        user = get_object_or_404(User, pk=uid)
        context = {
            'uobj': user,
        }
        return self.render_to_response(self.template_path, context)


class UserCreateView(GenericView):
    template_path = 'config/users-create.html'
    menu = ['users']

    @login_required
    @staff_required
    def get(self, request):
        form = forms.UserEditForm()
        context = {'form': form}
        return self.render_to_response(self.template_path, context)

    @login_required
    @staff_required
    def post(self, request):
        form = forms.UserEditForm(request.POST)
        if form.is_valid():
            user = form.save(commit=True)
            return self.render_redirect(reverse('web:users-view', args=[user.id]))

        context = {'form': form}
        return self.render_to_response(self.template_path, context)


class UserEditView(GenericView):
    template_path = 'config/users-edit.html'
    menu = ['users']
    
    @login_required
    @staff_required
    def get(self, request, uid):
        user = get_object_or_404(User, pk=uid)
        form = forms.UserEditForm(instance=user)

        context = {
            'uobj': user,
            'form': form,
        }
        return self.render_to_response(self.template_path, context)

    @login_required
    @staff_required
    def post(self, request, uid):
        user = get_object_or_404(User, pk=uid)
        form = forms.UserEditForm(request.POST, instance=user)
        
        if form.is_valid():
            form.save()
            messages.info(request, _(u"User saved succesful"))
            return self.render_redirect(reverse('web:users-edit', args=[user.id]))

        contex = {
            'uobj': user,
            'form': form,
        }
        return self.render_to_response(self.template_path, context)


class UserDelete(GenericView):
    template_path = 'config/users-delete.html'
    menu = ['users']

    def get_context(self):
        user = get_object_or_404(User, pk=self.kwargs['uid'])
        return {'uobj':user}

    @login_required
    @staff_required
    def get(self, request, uid):
        context = self.get_context()
        return self.render_to_response(self.template_path, context)

    @login_required
    @staff_required
    def post(self, request, uid):
        context = self.get_context()
        context['uobj'].delete()
        return self.render_redirect(reverse('web:users'))


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
        project = get_object_or_404(models.Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', ('view', 'edit')),
        ])

        user_story = get_object_or_404(project.user_stories, ref=iref)

        form = forms.UserStoryFormInline(instance=user_story)
        context = {'form': form}
        return self.render_to_response(self.template_name, context)

    @login_required
    def post(self, request, pslug, iref):
        project = get_object_or_404(models.Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', ('view', 'edit')),
        ])

        user_story = get_object_or_404(project.user_stories, ref=iref)

        form = forms.UserStoryFormInline(request.POST, instance=user_story)
        
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


class WikiPageView(GenericView):
    menu = ['wiki']
    template_path = 'wiki-page.html'

    @login_required
    def get(self, request, pslug, wslug):
        project = get_object_or_404(models.Project, slug=pslug)
        
        self.check_role(request.user, project, [
            ('project', 'view'),
            ('wiki', 'view'),
        ])
        
        try:
            wikipage = project.wiki_pages.get(slug=wslug)
        except models.WikiPage.DoesNotExist:
            return self.render_redirect(reverse('web:wiki-page-edit', 
                args=[project.slug, wslug]))

        context = {
            'project': project,
            'wikipage': wikipage,
        }
        return self.render_to_response(self.template_path, context)


class WikiPageEditView(GenericView):
    menu = ['wiki']
    template_path = 'wiki-page-edit.html'

    @login_required
    def get(self, request, pslug, wslug):
        project = get_object_or_404(models.Project, slug=pslug)
        
        self.check_role(request.user, project, [
            ('project', 'view'),
            ('wiki', ('view', 'create', 'edit')),
        ])

        try:
            wikipage = project.wiki_pages.get(slug=wslug)
        except models.WikiPage.DoesNotExist:
            wikipage = None

        form = forms.WikiPageEditForm(instance=wikipage)

        context = {
            'form': form,
            'project': project,
        }

        return self.render_to_response(self.template_path, context)

    @login_required
    def post(self, request, pslug, wslug):
        project = get_object_or_404(models.Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('wiki', ('view', 'create', 'edit')),
        ])

        try:
            wikipage = project.wiki_pages.get(slug=wslug)
        except models.WikiPage.DoesNotExist:
            wikipage = None

        form = forms.WikiPageEditForm(request.POST, instance=wikipage)
        if form.is_valid():
            wikipage_new = form.save(commit=False)

            if wikipage is not None:
                old_wikipage = models.WikiPage.objects.get(pk=wikipage.pk)
                history_entry = models.WikiPageHistory(
                    wikipage = old_wikipage,
                    content = old_wikipage.content,
                    owner = old_wikipage.owner,
                    created_date = old_wikipage.created_date,
                )
                history_entry.save()
            
            if not wikipage_new.slug:
                wikipage_new.slug = models.slugify_uniquely(wslug, wikipage_new.__class__)

            if not wikipage_new.project_id:
                wikipage_new.project = project

            wikipage_new.owner = request.user
            wikipage_new.save()
            return self.render_redirect(wikipage_new.get_view_url())

        context = {
            'form': form,
            'project': project,
        }
        return self.render_to_response(self.template_path, context)


class WikiPageHistory(GenericView):
    menu = ['wiki']
    template_path = 'wiki-page-history.html'

    @login_required
    def get(self, request, pslug, wslug):
        project = get_object_or_404(models.Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('wiki', 'view'),
        ])

        wikipage = get_object_or_404(project.wiki_pages, slug=wslug)

        context = {
            'entries': wikipage.history_entries.order_by('created_date'),
            'wikipage': wikipage,
            'project': project,
        }

        return self.render_to_response(self.template_path, context)


class WikiPageHistoryView(GenericView):
    menu = ['wiki']
    template_path = 'wiki-page-history-view.html'
    
    @login_required
    def get(self, request, pslug, wslug, hpk):
        project = get_object_or_404(models.Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('wiki', 'view'),
        ])

        wikipage = get_object_or_404(project.wiki_pages, slug=wslug)
        history_entry = get_object_or_404(wikipage.history_entries, pk=hpk)
        
        context = {
            'project': project,
            'wikipage': wikipage,
            'history_entry': history_entry,
        }
        return self.render_to_response(self.template_path, context)


class WikipageDeleteView(GenericView):
    template_path = 'wiki-page-delete.html'

    def get_context(self):
        project = get_object_or_404(models.Project, slug=self.kwargs['pslug'])

        self.check_role(self.request.user, project, [
            ('project', 'view'),
            ('wiki', ('view', 'delete')),
        ])

        wikipage = get_object_or_404(project.wiki_pages, slug=self.kwargs['wslug'])

        context = {
            'project': project,
            'wikipage': wikipage,
        }
        return context

    @login_required
    def get(self, request, **kwargs):
        context = self.get_context()
        return self.render_to_response(self.template_path, context)
    
    @login_required
    def post(self, request, **kwargs):
        context = self.get_context()
        context['wikipage'].history_entries.all().delete()
        context['wikipage'].delete()

        return self.render_redirect(reverse('web:wiki-page',
            args = [context['project'].slug, 'home']))
