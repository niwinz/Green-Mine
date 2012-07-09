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
