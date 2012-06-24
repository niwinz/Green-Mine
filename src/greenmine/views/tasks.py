# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.template import loader
from django.db.models import Q
from django.db import transaction

from greenmine.core.generic import GenericView
from greenmine.core.decorators import login_required
from greenmine import models
from greenmine.forms import base as forms
from greenmine.core.utils import iter_points
from greenmine.forms.tasks import TaskCreateForm
from greenmine.forms.base import CommentForm

from .issues import IssueList

class TaskList(IssueList):
    template_name = 'tasks.html'
    menu = ['tasks']

    def get_query_set(self, milestone):
        user_stories = milestone.user_stories.all()
        return milestone.tasks.filter(type="task")


class CreateTask(GenericView):
    template_name = "tasks-create.html"
    menu = ['tasks']

    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', 'view'),
            ('task', ('view', 'create')),
        ])

        form = TaskCreateForm(project=project)

        return self.render_to_response(self.template_name, {
            "form": form,
            "project": project,
        })

    @login_required
    @transaction.commit_on_success
    def post(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', 'view'),
            ('task', ('view', 'create')),
        ])

        form = TaskCreateForm(request.POST, project=project)
        if not form.is_valid():
            return self.render_json_error(form.errors)

        task = form.save(commit=False)
        task.type = 'task'
        task.project = project
        task.owner = request.user
        task.save()

        #milestone_pk = task.user_story.milestone \
        #    and task.user_story.milestone.pk \
        #    or request.GET.get('milestone', None) \
        #    or project.milestones.order_by('-created_date')[0].pk

        redirect_to = reverse('tasks-list', args=[project.slug])
        return self.render_to_ok({"task": task.to_dict(), 'redirect_to':redirect_to})



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
        _old_us = task.user_story

        if form.is_valid():
            task = form.save(commit=True)
            signals.mail_task_modified.send(sender=self, task=task, user=request.user)

            if task.assigned_to and task.assigned_to.pk != _old_assigned_to_pk:
                signals.mail_task_assigned.send(sender=self, task=task, user=request.user)

            if _old_us and not task.user_story:
                _old_us.update_status()
            elif not _old_us and task.user_story:
                task.user_story.update_status()

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


class TaskSendComment(GenericView):
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

        html = loader.render_to_string("tasks-view-change-part.html", {
            "change": change_instance,
            "project": project,
        })

        return self.render_to_ok({"html":html})
