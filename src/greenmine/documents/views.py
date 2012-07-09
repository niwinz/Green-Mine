# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.template import loader
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.views.decorators.csrf import ensure_csrf_cookie

from ..core.generic import GenericView
from ..core.decorators import login_required
from ..core import signals
from ..scrum.models import Project

from .models import Document
from .forms import DocumentForm

from datetime import timedelta
import os, re


class Documents(GenericView):
    template_path = 'documents.html'
    menu = ['documents']

    # TODO: fix permissions

    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
        ])

        documents = project.documents.order_by('-created_date')

        context = {
            'documents': documents,
            'project': project,
            'form': DocumentForm(),
        }

        return self.render_to_response(self.template_path, context)

    @login_required
    def post(self, request, pslug):
        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
        ])

        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = Document.objects.create(
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
        project = get_object_or_404(Project, slug=pslug)
        document = get_object_or_404(project.documents, pk=docid)

        document.delete()
        return self.render_to_ok()
