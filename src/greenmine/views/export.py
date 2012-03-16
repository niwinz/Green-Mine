# -*- coding: utf-8 -*-
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.template import RequestContext, loader
from django.contrib import messages
from django.db.utils import IntegrityError
from django.db import transaction
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson
from django.utils.encoding import force_unicode
from django.views.decorators.cache import cache_page

from greenmine.views.generic import GenericView
from greenmine.views.decorators import login_required, staff_required
from greenmine import models, forms, utils

import shutil
import pickle
import copy
import os
import re
import io


class BinaryFile(object):
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self._file = io.open(self.name, mode='w+b')
        return self._file

    def __exit__(self, exc_type, exc_value, traceback):
        self._file.flush()
        self._file.close()


class ProjectExportView(GenericView):
    template_path = 'config/project-export.html'
    menu = ['settings', 'export']

    def backup_path_list(self):
        for path in os.listdir(settings.BACKUP_PATH):
            if os.path.splitext(path)[1] != '.xz':
                continue

            yield os.path.join(settings.BACKUP_PATH, path)

    def backup_file_list(self):
        for path in self.backup_path_list():
            yield path, os.path.basename(path), os.path.getsize(path)


    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        
        context = {
            'project': project,
            'flist': self.backup_file_list()
        }

        return self.render_to_response(self.template_path, context)


import base64

class ProjectExportNow(ProjectExportView):
    def _clean_copy(self, obj):
        new_object = copy.deepcopy(obj)

        if "_state" in new_object:
            del new_object["_state"]

        return new_object

    def create_tempdir_for_project(self, project):
        dirname = u"{0}_backup".format(project.slug)

        self.path = os.path.join(settings.BACKUP_PATH, dirname)

        if os.path.exists(self.path):
            shutil.rmtree(self.path)

        os.mkdir(self.path)

    def _backup_project_data(self, project):
        filename = "project-data.data"
        filepath = os.path.join(self.path, filename)

        with io.open(filepath, 'w+b') as f:
            obj = self._clean_copy(project.__dict__)
            pickle.dump(obj, f, -1)
        
        filename = 'project-owner.data'
        filepath = os.path.join(self.path, filename)

        with io.open(filepath, 'w+b') as f:
            obj = self._clean_copy(project.owner.__dict__)
            pickle.dump(obj, f, -1)

    def _backup_user_roles(self, project):
        directory_pathname = "user_roles"
        path = os.path.join(self.path, directory_pathname)

        if os.path.exists(path):
            shutil.rmtree(path)

        os.mkdir(path)

        for pur in models.ProjectUserRole.objects.filter(project=project):
            obj = self._clean_copy(pur.__dict__)

            filename = "{0}_{1}.data".format(pur.id, project.id)
            filepath = os.path.join(path, filename)

            with BinaryFile(filepath) as f:
                pickle.dump(obj, f, -1)

    def _backup_milestones(self, project):
        directory_pathname = "milestones"
        path = os.path.join(self.path, directory_pathname)

        if os.path.exists(path):
            shutil.rmtree(path)

        os.mkdir(path)

        for milestone in project.milestones.all():
            obj = self._clean_copy(milestone.__dict__)

            filename = "{0}_{1}.data".format(milestone.id, project.id)
            filepath = os.path.join(path, filename)

            with BinaryFile(filepath) as f:
                pickle.dump(obj, f, -1)

    def _backup_user_story(self, project):
        directory_pathname = "user_stories"
        path = os.path.join(self.path, directory_pathname)

        if os.path.exists(path):
            shutil.rmtree(path)

        os.mkdir(path)
        
        for user_story in project.user_stories.all():
            obj = self._clean_copy(user_story.__dict__)
            obj['watchers'] = [o.id for o in user_story.watchers.all().distinct()]

            filename = "{0}_{1}.data".format(user_story.id, project.id)
            filepath = os.path.join(path, filename)

            with BinaryFile(filepath) as f:
                pickle.dump(obj, f, -1)

    def _backup_tasks(self, project):
        directory_pathname = "tasks"
        path = os.path.join(self.path, directory_pathname)

        if os.path.exists(path):
            shutil.rmtree(path)

        os.mkdir(path)

        for task in project.tasks.all():
            obj = self._clean_copy(task.__dict__)
            obj['watchers'] = [o.id for o in task.watchers.all()]

            filename = "task_{0}_{1}.data".format(task.id, project.id)
            filepath = os.path.join(path, filename)

            with BinaryFile(filepath) as f:
                pickle.dump(obj, f, -1)

        for response in models.TaskResponse.objects.filter(task__in=project.tasks.all()):
            obj = self._clean_copy(response.__dict__)
            obj['watchers'] = [o.id for o in task.watchers.all()]

            filename = "response_{0}_{1}.data".format(response.id, project.id)
            filepath = os.path.join(path, filename)

            with BinaryFile(filepath) as f:
                pickle.dump(obj, f, -1)
        
        import zlib
        for res_file in models.TaskAttachedFile.objects.filter(task__in=project.tasks.all()):
            obj = self._clean_copy(res_file.__dict__)
            raw_file_data = res_file.attached_file.read()
            raw_file_data = zlib.compress(raw_file_data, 9)
            raw_file_data = base64.b64encode(raw_file_data)
            obj['__raw_file_data'] = raw_file_data

            filename = "file_response_{0}_{1}.data".format(res_file.id, project.id)
            filepath = os.path.join(path, filename)

            with BinaryFile(filepath) as f:
                pickle.dump(obj, f, -1)


    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        self.create_tempdir_for_project(project)
        self._backup_project_data(project)
        self._backup_user_roles(project)
        self._backup_milestones(project)
        self._backup_user_story(project)
        self._backup_tasks(project)

        return self.redirect_referer("Now exported")
