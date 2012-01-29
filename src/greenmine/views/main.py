# -*- coding: utf-8 -*-

from django.views.decorators.cache import cache_page
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode
from django.http import HttpResponseRedirect, HttpResponse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.core.mail import EmailMessage
from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.template import RequestContext, loader
from django.contrib import messages
from django.db.utils import IntegrityError
from django.db import transaction
from django.utils.decorators import method_decorator
from django.utils import simplejson
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.cache import cache

from greenmine.views.generic import GenericView, ProjectGenericView
from greenmine.views.decorators import login_required
from greenmine import models, forms


from django.contrib.auth.models import User

import re

class LoginView(GenericView):
    """ Login view """
    template_name = 'login.html'
    
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        login_form = forms.LoginForm(request=request)

        return self.render(self.template_name, 
            {'form': login_form})

    def post(self, request):
        login_form = forms.LoginForm(request.POST, request=request)
        if login_form.is_valid():
            user_profile = login_form._user.get_profile()
            if user_profile.default_language:
                request.session['django_language'] = user_profile.default_language

            return self.render_redirect("/")

        return self.render_to_response(self.template_name,
            {'form': login_form})
           

class PasswordRecoveryView(GenericView):
    template_name = "password_recovery.html"

    def get(self, request, token):
        form = forms.PasswordRecoveryForm()
        context = {'form':form}
        return self.render(self.template_name, context)

    def post(self, request, token):
        form = forms.PasswordRecoveryForm(request.POST)
        if form.is_valid():
            email = cache.get("fp_%s" % token)
            if not email:
                messages.error(request, _(u'Token has expired, try again'))
                return self.redirect(reverse('web:login'))

            user = models.User.objects.get(email=email)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.info(request, _(u'The password has been successfully restored.'))

            cache.delete("fp_%s" % token)
            return self.redirect(reverse('web:login'))

        context = {'form':form}
        return self.render(self.template_name, context)


class HomeView(GenericView):
    """ General user projects view """
    template_name = 'projects.html'
    menu = ['projects']

    @login_required
    def get(self, request, *args, **kwargs):
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
        
        projects = request.user.projects.all()
        paginator = Paginator(projects, 20)
        page = paginator.page(page)

        context = {
            'is_paginated': True if paginator.count else False,
            'page': page,
            'projects': projects,
        }
        return self.render(self.template_name, context)
    

class BacklogView(GenericView):
    """ General dasboard view,  with all milestones and all tasks. """
    template_name = 'backlog.html'
    menu = ['backlog']

    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        unassigned = project.user_stories.filter(milestone__isnull=True)\
            .order_by('-priority')

        form_new_milestone = forms.MilestoneForm()
        
        context = {
            'project': project,
            'milestones': project.milestones.order_by('-created_date'),
            'unassigned_us': unassigned,
            'form_new_milestone': form_new_milestone,
        }

        return self.render(self.template_name, context)


class TasksView(GenericView):
    """ 
    General dasboard view,  with all milestones and all tasks. 
    """

    template_name = 'tasks.html'
    menu = ['tasks']

    @login_required
    def get(self, request, pslug, mid=None):
        project = get_object_or_404(models.Project, slug=pslug)

        if mid is None:
            return self.render_redirect(project.get_default_tasks_url())

        milestone = get_object_or_404(project.milestones, pk=mid)
        tasks = milestone.tasks.all()

        context = {
            'project': project,
            'milestones': project.milestones.order_by('-created_date'),
            'milestone': milestone,
            'tasks': tasks,
        }

        return self.render(self.template_name, context)


class DashboardView(GenericView):
    template_name = 'dashboard.html'
    menu = ['dashboard']

    @login_required
    def get(self, request, pslug, mid=None):
        project = get_object_or_404(models.Project, slug=pslug)

        milestones = project.milestones.order_by('-created_date')
        milestone = milestones.get(pk=mid) if mid is not None else milestones[0]

        if mid is None:
            return self.render_redirect(milestone.get_dashboard_url())

        context = {
            'uss':milestone.user_stories.all(),
            'milestones': milestones,
            'milestone':milestone,
            'project': project,
        }
        return self.render(self.template_name, context)


class ProjectCreateView(GenericView):
    template_name = 'project-create.html'
    user_rx = re.compile(r'^user_(?P<userid>\d+)$', flags=re.U)
    menu = ['projects']

    def parse_roles(self):
        user_role = {}

        for post_key in self.request.POST.keys():
            user_rx_pos = self.user_rx.match(post_key)
            if not user_rx_pos:
                continue

            user_role[user_rx_pos.group('userid')] = self.request.POST[post_key]

        role_values = dict(models.ROLE_CHOICES).keys()
        invalid_role = False
        for role in user_role.values():
            if role not in role_values:
                invalid_role = True
                break
            
        return {} if invalid_role else user_role

    def get(self, request):
        form = forms.ProjectForm()
        context = {'form':form, 'roles': models.ROLE_CHOICES}
        return self.render(self.template_name, context)

    def post(self, request):
        form = forms.ProjectForm(request.POST, request=request)
        context = {'form': form, 'roles': models.ROLE_CHOICES}
        
        if not form.is_valid():
            return self.render(self.template_name, context)
        
        sem = transaction.savepoint()
        try:
            user_role = self.parse_roles()
            if not user_role:
                transaction.savepoint_rollback(sem)
                emsg = _(u'You must specify at least one person to the project')
                messages.error(request, emsg)
                return self.render(self.template_name, context)
            
            project = form.save()
            for userid, role in user_role.iteritems():
                models.ProjectUserRole.objects.create(
                    project = project,
                    user = models.User.objects.get(pk=userid),
                    role = role
                )

        except Exception as e:
            transaction.savepoint_rollback(sem)
            messages.error(request, _(u'Integrity error: %(e)s') % {'e':unicode(e)})
            return self.render(self.template_name, {'form': form})
        
        transaction.savepoint_commit(sem)
        messages.info(request, _(u'Project %(pname)s is successful saved.') % {'pname':project.name})
        return HttpResponseRedirect(reverse('web:projects'))

    @login_required
    def dispatch(self, *args, **kwargs):
        return super(ProjectCreateView, self).dispatch(*args, **kwargs)


class ProjectEditView(ProjectCreateView):
    template_name = 'project-edit.html'
    user_rx = re.compile(r'^user_(?P<userid>\d+)$', flags=re.U)

    @login_required
    def get(self, request, pslug):		
        project = get_object_or_404(models.Project, slug=pslug)
        form = forms.ProjectForm(instance=project)
        context = {'form':form, 'roles': models.ROLE_CHOICES, 'project': project}
        return self.render(self.template_name, context)

    @login_required
    def post(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        form = forms.ProjectForm(request.POST, request=request, instance=project)
        context = {'form': form, 'roles': models.ROLE_CHOICES, 'project': project}
        
        if not form.is_valid():
            return self.render(self.template_name, context)
        
        sem = transaction.savepoint()
        try:
            user_role = self.parse_roles()
            if not user_role:
                transaction.savepoint_rollback(sem)
                emsg = _(u'You must specify at least one person to the project')
                messages.error(request, emsg)
                return self.render(self.template_name, context)

            project = form.save()
            models.ProjectUserRole.objects.filter(project=project).delete()
            for userid, role in user_role.iteritems():
                models.ProjectUserRole.objects.create(
                    project = project,
                    user = User.objects.get(pk=userid),
                    role = role
                )

        except Exception as e:
            transaction.savepoint_rollback(sem)
            messages.error(request, _(u'Integrity error: %(e)s') % {'e':unicode(e)})
            return self.render(self.template_name, {'form': form})
        
        transaction.savepoint_commit(sem)
        messages.info(request, _(u'Project %(pname)s is successful saved.') % {'pname':project.name})
        return HttpResponseRedirect(reverse('web:projects'))


class MilestoneCreateView(GenericView):
    template_name = 'milestone-create.html'
    menu = []

    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        form = forms.MilestoneForm()

        context = {
            'form': form,
            'project': project,
        }

        return self.render_to_response(self.template_name, context)

    @login_required
    def post(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        form = forms.MilestoneForm(request.POST)
        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.project = project
            milestone.save()
            return self.render_redirect(project.get_backlog_url())

        context = {
            'form': form,
            'project': project,
        }
        return self.render_to_response(self.template_name, context)


class UserStoryView(GenericView):
    template_name = "user-story-view.html"

    @login_required
    def get(self, request, pslug, iref):
        """ View US Detail """
        project = get_object_or_404(models.Project, slug=pslug)
        user_story = get_object_or_404(project.user_stories, ref=iref)
        form = forms.UserStoryCommentForm()
        
        context = {
            'user_story':user_story,
            'form': form, 
            'milestone':user_story.milestone,
            'project': project,
        }
        return self.render(self.template_name, context)

    #@login_required
    #def post(self, request, pslug, iref):
    #    """ Add comments method """
    #    project = get_object_or_404(models.Project, slug=pslug)
    #    user_story = get_object_or_404(project.user_stories, ref=iref)
    #    form = forms.UserStoryCommentForm(request.POST, \
    #                request.FILES, user_story=user_story, request=request)

    #    if form.is_valid():
    #        form.save()
    #        return HttpResponseRedirect(user_story.get_view_url())

    #    context = {'form':form, 'user_story':user_story}
    #    return self.render(self.template_name, context)


class UserStoryCreateView(GenericView):
    template_name = "user-story-create.html"

    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        form = forms.UserStoryForm()
        context = {
            'form':form, 
            'project':project,
        }
        return self.render(self.template_name, context)

    @login_required
    def post(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        form = forms.UserStoryForm(request.POST)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.milestone = None
            instance.owner = request.user
            instance.project = project
            instance.save()
            messages.info(request, _(u'The user story was created correctly'))
            return self.render_redirect(project.get_backlog_url())
    
        context = {
            'form':form, 
            'project':project,
        }
        return self.render(self.template_name, context)


class UserStoryEditView(GenericView):
    template_name = "user-story-edit.html"

    @login_required
    def get(self, request, pslug, iref):
        project = get_object_or_404(models.Project, slug=pslug)
        user_story = get_object_or_404(project.user_stories, ref=iref)

        form = forms.UserStoryForm(instance=user_story)
        context = {
            'project': project,
            'user_story': user_story,
            'form': form,
        }
        return self.render(self.template_name, context)

    @login_required
    def post(self, request, pslug, iref):
        project = get_object_or_404(models.Project, slug=pslug)
        user_story = get_object_or_404(project.user_stories, ref=iref)

        form = forms.UserStoryForm(request.POST, instance=user_story)
        if form.is_valid():
            user_story = form.save(commit=True)
            messages.info(request, _(u'The user story has been successfully saved'))
            return self.redirect(user_story.get_view_url())

        context = {
            'project': project,
            'user_story': user_story,
            'form': form,
        }
        return self.render(self.template_name, context)


class UserStoryDeleteView(GenericView):
    template_name = "user-story-delete.html"

    @login_required
    def get(self, request, pslug, iref):
        project = get_object_or_404(models.Project, slug=pslug)
        user_story = get_object_or_404(project.user_stories, ref=iref)

        context = {
            'project': project,
            'user_story': user_story,
        }
        return self.render(self.template_name, context)
    
    @login_required
    def post(self, request, pslug, iref):
        project = get_object_or_404(models.Project, slug=pslug)
        user_story = get_object_or_404(project.user_stories, ref=iref)

        if user_story.milestone:
            response = self.redirect(user_story.milestone.get_dashboard_url())
        else:
            response = self.redirect(project.get_unassigned_dashboard_url())

        user_story.delete()
        return response


class TaskCreateView(GenericView):
    template_name = 'task-create.html'

    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        milestone = None

        mid = request.GET.get('milestone', None)
        if mid is not None:
            milestoneqs = project.milestones.filter(pk=mid)
            milestone = milestoneqs and milestoneqs.get() or None

        form = forms.TaskForm(project=project, initial_milestone=milestone)
        context = {
            'project': project,
            'form': form,
        }
        return self.render(self.template_name, context)

    @login_required
    def post(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        milestone = None

        mid = request.GET.get('milestone', None)
        if mid is not None:
            milestoneqs = project.milestones.filter(pk=mid)
            milestone = milestoneqs and milestoneqs.get() or None

        form = forms.TaskForm(request.POST, project=project, initial_milestone=milestone)
        next_url = request.GET.get('next', None)

        if form.is_valid():
            task = form.save(commit=False)
            task.owner = request.user
            task.project = project
            task.save()
            
            messages.info(request, _(u"The task has been created with success!"))
            if next_url:
                # TODO fix security
                return self.redirect(next_url)
            
            return self.redirect(task.milestone.get_tasks_url())

        context = {
            'project': project,
            'user_story': user_story,
            'form': form,
        }
        return self.render(self.template_name, context)


class TaskEditView(GenericView):
    template_name = 'task_edit.html'

    @login_required
    def get(self, request, pslug, iref, tref):
        project = get_object_or_404(models.Project, slug=pslug)
        user_story = get_object_or_404(project.user_stories, ref=iref)
        task = get_object_or_404(user_story.tasks, ref=tref)
        form = forms.TaskForm(instance=task)

        context = {
            'project': project,
            'user_story': user_story,
            'task': task,
            'form': form,
        }
        return self.render(self.template_name, context)
    
    @login_required
    def post(self, request, pslug, iref, tref):
        project = get_object_or_404(models.Project, slug=pslug)
        user_story = get_object_or_404(project.user_stories, ref=iref)
        task = get_object_or_404(user_story.tasks, ref=tref)
        form = forms.TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()

            messages.info(request, _(u"The task has been created with success!"))
            return self.redirect(user_story.get_view_url())

        context = {
            'project': project,
            'user_story': user_story,
            'task': task,
            'form': form,
        }
        return self.render(self.template_name, context)
