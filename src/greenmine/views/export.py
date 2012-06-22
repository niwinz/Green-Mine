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
from django.utils.encoding import force_unicode
from django.views.decorators.cache import cache_page

from greenmine.views.generic import GenericView
from greenmine.views.decorators import login_required, staff_required
from greenmine import models, forms, utils

import datetime
import subprocess
import shutil
import pickle
import base64
import zlib
import copy
import sys
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


    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)

        context = {
            'project': project,
            'flist': models.ExportDirectoryCache.objects.all()
        }

        return self.render_to_response(self.template_path, context)


class RehashExportsDirectory(GenericView):
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
        models.ExportDirectoryCache.objects.all().delete()

        for path, name, size in self.backup_file_list():
            models.ExportDirectoryCache.objects.create(
                path = name,
                size = size,
            )

        return self.redirect_referer(_(u"Now rehashed"))


class PerojectImportNow(GenericView):
    @login_required
    def get(self, request, project, iid):
        project = get_object_or_404(models.Project, slug=pslug)


class ProjectExportNow(GenericView):
    def _clean_copy(self, obj):
        new_object = copy.deepcopy(obj)

        if "_state" in new_object:
            del new_object["_state"]

        return new_object

    def create_tempdir_for_project(self, project):
        self.dirname = u"{0}_backup".format(project.slug)
        self.path = os.path.join(settings.BACKUP_PATH, self.dirname)

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

        #for response in models.TaskResponse.objects.filter(task__in=project.tasks.all()):
        #    obj = self._clean_copy(response.__dict__)
        #    obj['watchers'] = [o.id for o in task.watchers.all()]

        #    filename = "response_{0}_{1}.data".format(response.id, project.id)
        #    filepath = os.path.join(path, filename)

        #    with BinaryFile(filepath) as f:
        #        pickle.dump(obj, f, -1)
        #
        #for res_file in models.TaskAttachedFile.objects.filter(task__in=project.tasks.all()):
        #    obj = self._clean_copy(res_file.__dict__)
        #    raw_file_data = res_file.attached_file.read()
        #    raw_file_data = zlib.compress(raw_file_data, 9)
        #    raw_file_data = base64.b64encode(raw_file_data)
        #    obj['__raw_file_data'] = raw_file_data

        #    filename = "file_response_{0}_{1}.data".format(res_file.id, project.id)
        #    filepath = os.path.join(path, filename)

        #    with BinaryFile(filepath) as f:
        #        pickle.dump(obj, f, -1)

    def _backup_questions(self, project):
        directory_pathname = "questions"
        path = os.path.join(self.path, directory_pathname)

        if os.path.exists(path):
            shutil.rmtree(path)

        os.mkdir(path)

        for question in project.questions.all():
            obj = self._clean_copy(question.__dict__)
            obj['watchers'] = [o.id for o in question.watchers.all()]

            filename = "{0}_{1}.data".format(question.id, project.id)
            filepath = os.path.join(path, filename)

            with BinaryFile(filepath) as f:
                pickle.dump(obj, f, -1)

        for response in models.QuestionResponse.objects\
                        .filter(question__in=project.questions.all()):
            obj = self._clean_copy(question.__dict__)
            raw_file_data = response.attached_file.read()
            raw_file_data = zlib.compress(raw_file_data, 9)
            raw_file_data = base64.b64encode(raw_file_data)
            obj['__raw_file_data'] = raw_file_data

            filename = "file_response_{0}_{1}.data".format(response.id, project.id)
            filepath = os.path.join(path, filename)

            with BinaryFile(filepath) as f:
                pickle.dump(obj, f, -1)

    def _backup_wiki(self, project):
        directory_pathname = "wiki"
        path = os.path.join(self.path, directory_pathname)

        if os.path.exists(path):
            shutil.rmtree(path)

        os.mkdir(path)

        for wikipage in project.wiki_pages.all():
            obj = self._clean_copy(wikipage.__dict__)
            obj['watchers'] = [o.id for o in wikipage.watchers.all()]

            filename = "{0}_{1}.data".format(wikipage.id, project.id)
            filepath = os.path.join(path, filename)

            with BinaryFile(filepath) as f:
                pickle.dump(obj, f, -1)

        for fattached in models.WikiPageAttachment.objects\
                        .filter(wikipage__in=project.wiki_pages.all()):

            obj = self._clean_copy(fattached.__dict__)
            raw_file_data = fattached.attached_file.read()
            raw_file_data = zlib.compress(raw_file_data, 9)
            raw_file_data = base64.b64encode(raw_file_data)
            obj['__raw_file_data'] = raw_file_data

            filename = "file_response_{0}_{1}.data".format(fattached.id, project.id)
            filepath = os.path.join(path, filename)

            with BinaryFile(filepath) as f:
                pickle.dump(obj, f, -1)

    def _create_tarball(self, project):
        current_date = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%s")
        filename = "{0}-{1}.tar.xz".format(project.slug, current_date)
        current_pwd = os.getcwd()
        os.chdir(settings.BACKUP_PATH)
        command = "tar cvJf {0} {1}".format(filename, self.dirname)
        p = subprocess.Popen(command.split(), stdout=sys.stdout)
        os.chdir(current_pwd)

    @login_required
    def get(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        self.create_tempdir_for_project(project)
        self._backup_project_data(project)
        self._backup_user_roles(project)
        self._backup_milestones(project)
        self._backup_user_story(project)
        self._backup_tasks(project)
        self._backup_questions(project)
        self._backup_wiki(project)
        self._create_tarball(project)
        return self.redirect_referer("Now exported, rehash directory!")
