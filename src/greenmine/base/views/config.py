# -*- coding: utf-8 -*-

from django.views.generic import View
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
from django.utils.decorators import method_decorator
from django.db import transaction

from greenmine.core.generic import GenericView
from greenmine.core.decorators import login_required
from greenmine import models

from django.core import serializers

import zipfile
import json

from StringIO import StringIO

class AdminProjectExport(GenericView):
    def serialize(self, objects):
        return serializers.serialize("json", objects, indent=4, \
                                                use_natural_keys=True)

    def get(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)

        tmpfile = StringIO()
        zfile = zipfile.ZipFile(tmpfile, 'a')

        # Collect data
        project_data = self.serialize([project])
        milestones_data = self.serialize(project.milestones.all())
        user_stories = self.serialize(project.user_stories.all())

        tasks  = self.serialize(project.tasks.all())
        pur_qs = models.ProjectUserRole.objects.filter(project=project)
        u_qs = pur_qs.values_list('user_id', flat=True)

        user_role = self.serialize(pur_qs)
        user = self.serialize(models.User.objects.filter(id__in=u_qs))

        zfile.writestr('project.json', project_data)
        zfile.writestr('milestones.json', milestones_data)
        zfile.writestr('us.json', user_stories)
        zfile.writestr('tasks.json', tasks)
        zfile.writestr('user_role.json', user_role)
        zfile.writestr('user.json', user)
        zfile.close()

        response = HttpResponse(tmpfile.getvalue(), mimetype='application/zip')
        response['Content-Disposition'] = \
                            'attachment; filename=%s-bkp.zip' % (project.slug)

        tmpfile.close()
        return response


class BackupContext(object):
    pass
