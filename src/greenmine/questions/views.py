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

from django.views.decorators.csrf import ensure_csrf_cookie

from greenmine.core.generic import GenericView
from greenmine.core.decorators import login_required, staff_required

# Temporal imports
from greenmine.base.models import *
from greenmine.scrum.models import *

from greenmine.forms.base import *
from greenmine.questions.forms import *
from greenmine.scrum.forms.project import *
from greenmine.scrum.forms.milestone import *
from greenmine.core.utils import iter_points
from greenmine.core import signals

import os
import re

from datetime import timedelta


class QuestionsListView(GenericView):
    template_path = 'questions.html'
    menu = ['questions']

    def get(self, request, pslug):
        project = get_object_or_404(Project, slug=pslug)
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
        project = get_object_or_404(Project, slug=pslug)
        form = QuestionCreateForm(project=project)

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
        project = get_object_or_404(Project, slug=pslug)
        form = QuestionCreateForm(request.POST, project=project)

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
        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('question', ('view', 'edit')),
        ])

        question = get_object_or_404(project.questions, slug=qslug)
        form = QuestionCreateForm(instance=question, project=project)

        context = {
            'form': form,
            'project': project,
            'question': question,
        }
        return self.render_to_response(self.template_path, context)

    @login_required
    def post(self, request, pslug, qslug):
        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('question', ('view', 'edit')),
        ])

        question = get_object_or_404(project.questions, slug=qslug)
        form = QuestionCreateForm(request.POST, instance=question, project=project)

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
        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('question', 'view'),
        ])

        question = get_object_or_404(project.questions, slug=qslug)
        form = QuestionResponseForm()

        context = {
            'form': form,
            'project': project,
            'question': question,
            'responses': question.responses.order_by('created_date'),
        }
        return self.render_to_response(self.template_path, context)

    @login_required
    def post(self, request, pslug, qslug):
        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('question', 'view'),
        ])

        question = get_object_or_404(project.questions, slug=qslug)
        form = QuestionResponseForm(request.POST)

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
        project = get_object_or_404(Project, slug=self.kwargs['pslug'])

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


