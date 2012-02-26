# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect, HttpResponse
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
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson
from django.utils.encoding import force_unicode
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.cache import cache_page

from greenmine.views.generic import GenericView, ProjectGenericView
from greenmine.views.decorators import login_required, staff_required
from greenmine import models, forms

import re

class LoginView(GenericView):
    """ Login view """
    template_name = 'login.html'
    
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        login_form = forms.LoginForm(request=request)

        return self.render_to_response(self.template_name, 
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


class PasswordChangeView(GenericView):
    """
    Password change view.
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


class PasswordRecoveryView(GenericView):
    template_name = "password_recovery.html"

    def get(self, request, token):
        form = forms.PasswordRecoveryForm()
        context = {'form':form}
        return self.render_to_response(self.template_name, context)

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
        return self.render_to_response(self.template_name, context)


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
        
        if request.user.is_staff:
            projects = models.Project.objects.order_by('name')
        else:
            projects = request.user.projects.all()

        paginator = Paginator(projects, 20)
        page = paginator.page(page)

        context = {
            'is_paginated': True if paginator.count else False,
            'page': page,
            'projects': projects,
        }
        return self.render_to_response(self.template_name, context)
    

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
            'milestones': project.milestones.order_by('-created_date').prefetch_related('project'),
            'unassigned_us': unassigned.select_related(),
            'form_new_milestone': form_new_milestone,
        }

        return self.render_to_response(self.template_name, context)


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

        return self.render_to_response(self.template_name, context)


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
        return self.render_to_response(self.template_name, context)


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
        return self.render_to_response(self.template_name, context)

    def post(self, request):
        form = forms.ProjectForm(request.POST, request=request)
        context = {'form': form, 'roles': models.ROLE_CHOICES}
        
        if not form.is_valid():
            return self.render_to_response(self.template_name, context)
        
        sem = transaction.savepoint()
        try:
            user_role = self.parse_roles()
            if not user_role:
                transaction.savepoint_rollback(sem)
                emsg = _(u'You must specify at least one person to the project')
                messages.error(request, emsg)
                return self.render_to_response(self.template_name, context)
            
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
            return self.render_to_response(self.template_name, {'form': form})
        
        transaction.savepoint_commit(sem)
        messages.info(request, _(u'Project %(pname)s is successful saved.') % {'pname':project.name})
        return HttpResponseRedirect(reverse('web:projects'))

    @login_required
    def dispatch(self, *args, **kwargs):
        return super(ProjectCreateView, self).dispatch(*args, **kwargs)


class ProjectEditView(ProjectCreateView):
    template_name = 'config/project-edit.html'
    user_rx = re.compile(r'^user_(?P<userid>\d+)$', flags=re.U)
    menu = ["settings", "editproject"]

    @login_required
    def get(self, request, pslug):		
        project = get_object_or_404(models.Project, slug=pslug)
        form = forms.ProjectForm(instance=project)
        
        print project.user_roles.all()
        context = {
            'form':form, 
            'roles': models.ROLE_CHOICES, 
            'project': project
        }
        return self.render_to_response(self.template_name, context)

    @login_required
    def post(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        form = forms.ProjectForm(request.POST, request=request, instance=project)
        context = {'form': form, 'roles': models.ROLE_CHOICES, 'project': project}
        
        if not form.is_valid():
            return self.render_to_response(self.template_name, context)
        
        sem = transaction.savepoint()
        try:
            user_role = self.parse_roles()
            if not user_role:
                transaction.savepoint_rollback(sem)
                emsg = _(u'You must specify at least one person to the project')
                messages.error(request, emsg)
                return self.render_to_response(self.template_name, context)

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
            return self.render_to_response(self.template_name, {'form': form})
        
        transaction.savepoint_commit(sem)
        messages.info(request, _(u'Project %(pname)s is successful saved.') % {'pname':project.name})
        return HttpResponseRedirect(project.get_edit_url())


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
        
        context = {
            'user_story':user_story,
            'milestone':user_story.milestone,
            'project': project,
        }
        return self.render_to_response(self.template_name, context)


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
        return self.render_to_response(self.template_name, context)

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
        return self.render_to_response(self.template_name, context)


class UserStoryEdit(GenericView):
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
        return self.render_to_response(self.template_name, context)

    @login_required
    def post(self, request, pslug, iref):
        project = get_object_or_404(models.Project, slug=pslug)
        user_story = get_object_or_404(project.user_stories, ref=iref)

        form = forms.UserStoryForm(request.POST, instance=user_story)
        if form.is_valid():
            user_story = form.save(commit=True)
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

        user_story.delete()
        return response


class TaskCreateView(GenericView):
    template_name = 'task-create.html'

    menu = ["tasks"]

    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        milestone = us = None

        mid = request.GET.get('milestone', None)
        if mid is not None:
            milestoneqs = project.milestones.filter(pk=mid)
            milestone = milestoneqs and milestoneqs.get() or None

        us = request.GET.get('us', None)
        if us is not None:
            usqs = project.user_stories.filter(pk=us)
            us = usqs and usqs.get() or None

        form = forms.TaskForm(project=project, 
            initial_milestone=milestone, initial_us=us)

        context = {
            'project': project,
            'form': form,
        }
        return self.render_to_response(self.template_name, context)

    @login_required
    def post(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        milestone = us = None

        mid = request.GET.get('milestone', None)
        if mid is not None:
            milestoneqs = project.milestones.filter(pk=mid)
            milestone = milestoneqs and milestoneqs.get() or None

        us = request.GET.get('us', None)
        if us is not None:
            usqs = project.user_stories.filter(pk=us)
            us = usqs and usqs.get() or None

        form = forms.TaskForm(request.POST, project=project, 
            initial_milestone=milestone, initial_us=us)

        next_url = request.GET.get('next', None)

        if form.is_valid():
            task = form.save(commit=False)
            task.owner = request.user
            task.project = project
            task.save()
            
            messages.info(request, _(u"The task has been created with success!"))
            if next_url:
                # TODO fix security
                return self.render_redirect(next_url)
            
            return self.render_redirect(task.milestone.get_tasks_url())

        context = {
            'project': project,
            'form': form,
        }
        return self.render_to_response(self.template_name, context)


class TaskView(GenericView):
    menu = ['tasks']
    template_path = 'task-view.html'

    @login_required
    def get(self, request, pslug, tref):
        project = get_object_or_404(models.Project, slug=pslug)
        task = get_object_or_404(project.tasks, ref=tref)
        form = forms.CommentForm(task=task, request=request)
        
        context = {
            'form': form,
            'task': task,
            'project': project,
        }

        return self.render_to_response(self.template_path, context)
    
    @login_required
    def post(self, request, pslug, tref):
        """ Add comments method """
        project = get_object_or_404(models.Project, slug=pslug)
        task = get_object_or_404(project.tasks, ref=tref)

        form = forms.CommentForm(request.POST, \
                    request.FILES, task=task, request=request)
        
        if form.is_valid():
            form.save()
            return self.render_redirect(task.get_view_url())

        context = {
            'form': form,
            'task': task,
            'project': project,
        }
        return self.render_to_response(self.template_path, context)


class TaskEdit(GenericView):
    template_path = 'task-edit.html'

    @login_required
    def get(self, request, pslug, tref):
        project = get_object_or_404(models.Project, slug=pslug)
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
        task = get_object_or_404(project.tasks, ref=tref)
        form = forms.TaskForm(request.POST, instance=task, project=project)

        next_url = request.GET.get('next', None)

        if form.is_valid():
            form.save()
            messages.info(request, _(u"The task has been saved!"))
            if next_url:
                return self.render_redirect(next_url)

            return self.render_redirect(task.get_view_url())

        context = {
            'project': project,
            'task': task,
            'form': form,
        }

        return self.render_to_response(self.template_name, context)


class AssignUs(GenericView):      
    template_name = 'milestone-item.html'
    
    @login_required
    def post(self, request, pslug, mid):
        project = get_object_or_404(models.Project, slug=pslug)
        user_story = get_object_or_404(project.user_stories, ref=request.POST.get('iref'))
        milestone = get_object_or_404(models.Milestone, id=mid)
        user_story.milestone = milestone
        user_story.save()
        
        context = {'us': user_story}
        
        return self.render_to_response(self.template_name, context)


class UnassignUs(GenericView):       
    template_name = 'user-story-item.html'   
    
    @login_required
    def post(self, request, pslug, iref):
        project = get_object_or_404(models.Project, slug=pslug)
        user_story = get_object_or_404(project.user_stories, ref=iref)
        user_story.milestone = None
        user_story.save()        
        
        context = {'us': user_story}
        return self.render_to_response(self.template_name, context)


class ProjectSettings(GenericView):
    template_path = "config/project.html"
    menu = ['settings', 'settings_general']

    def create_category_choices(self, project):
        return [('', '-----'),] + [(key, key.title()) \
            for key in project.meta_category_list]

    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        pur = get_object_or_404(project.user_roles, user=request.user)

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
            pur.meta_email_settings = form.emails_data
            pur.meta_category_color = form.colors_data
            pur.save()

            messages.info(request, _(u"Project preferences saved successfull"))
            return self.render_redirect(project.get_settings_url())

        context = {
            'pur': pur,
            'project': project,
            'form': form,
        }

        return self.render_to_response(self.template_path, context)


class QuestionsListView(GenericView):
    template_path = 'questions.html'
    menu = ['questions']

    def get(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        questions = project.questions.order_by('-created_date')

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
        form = forms.QuestionCreateForm()

        context = {
            'form': form,
            'project': project,
        }

        return self.render_to_response(self.template_path, context)
    
    @login_required
    def post(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        form = forms.QuestionCreateForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.project = project
            question.owner = request.user
            question.save()

            messages.info(request, _(u"Quienstion are created"))
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
        question = get_object_or_404(project.questions, slug=qslug)
        form = forms.QuestionCreateForm(instance=question)

        context = {
            'form': form,
            'project': project,
            'question': question,
        }
        return self.render_to_response(self.template_path, context)
    
    @login_required
    def post(self, request, pslug, qslug):
        project = get_object_or_404(models.Project, slug=pslug)
        question = get_object_or_404(project.questions, slug=qslug)
        form = forms.QuestionCreateForm(request.POST, instance=question)

        if form.is_valid():
            question = form.save(commit=False)
            question.save()

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
            if form.cleaned_data['reset_password']:
                # send mail
                pass

            return self.render_redirect()

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
    template_name = 'user_story_form_inline.html'
    us_template_name = 'user-story-item.html'
    
    @login_required
    def get(self, request, pslug, iref):
        project = get_object_or_404(models.Project, slug=pslug)
        user_story = get_object_or_404(project.user_stories, ref=iref)
        form = forms.UserStoryFormInline(instance=user_story)
        context = {
            'form': form
        }
        return self.render_to_response(self.template_name, context)

    @login_required
    def post(self, request, pslug, iref):
        project = get_object_or_404(models.Project, slug=pslug)
        user_story = get_object_or_404(project.user_stories, ref=iref)

        form = forms.UserStoryFormInline(request.POST, instance=user_story)
        
        if form.is_valid():
            form.save(commit=True)
            context = {
                'us': user_story,
                'project': project,
            }
            response_data = {
                'html': render_to_string(self.us_template_name, context,
                    context_instance=RequestContext(request))
            }
            return self.render_to_ok(response_data)

        return self.render_to_error(form.errors)


class WikiPageView(GenericView):
    menu = ['wiki']
    template_path = 'wiki-page.html'

    @login_required
    def get(self, request, pslug, wslug):
        project = get_object_or_404(models.Project, slug=pslug)
        
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

        try:
            wikipage = project.wiki_pages.get(slug=wslug)
        except models.WikiPage.DoesNotExist:
            wikipage = None

        form = forms.WikiPageEditForm(instance=wikipage)

        context = {
            'form': form,
        }

        return self.render_to_response(self.template_path, context)

    @login_required
    def post(self, request, pslug, wslug):
        project = get_object_or_404(models.Project, slug=pslug)
        try:
            wikipage = project.wiki_pages.get(slug=wslug)
        except models.WikiPage.DoesNotExist:
            wikipage = None

        form = forms.WikiPageEditForm(request.POST, instance=wikipage)
        if form.is_valid():
            wikipage = form.save(commit=False)
            if not wikipage.slug:
                wikipage.slug = models.slugify_uniquely(wslug, wikipage.__class__)

            wikipage.save()
            return self.render_redirect(wikipage.get_view_url())

        context = {
            'form': form,
        }
        return self.render_to_response(self.template_path, context)
