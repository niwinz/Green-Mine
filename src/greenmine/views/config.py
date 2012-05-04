# -*- coding: utf-8 -*-

from django.views.generic import View
from django.views.decorators.cache import cache_page
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode
from django.http import HttpResponseRedirect, HttpResponse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.core.mail import EmailMessage
from django.utils import simplejson
from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.template import RequestContext, loader
from django.contrib import messages
from django.db.utils import IntegrityError
from django.utils.decorators import method_decorator
from django.db import transaction

from .generic import GenericView
from .decorators import login_required
from .. import models, forms

from django.core import serializers
from django.utils import simplejson as json
import zipfile
from StringIO import StringIO

class AdminProjectsView(GenericView):
    def context(self):
        try:
            page = int(self.request.GET.get('page', '1'))
        except ValueError:
            page = 1
        
        projects = models.Project.objects.all()
        paginator = Paginator(projects, 20)
        page = paginator.page(page)
        return {
            'is_paginated': True if paginator.count else False,
            'page': page,
            'csel': 'projects',
        }

    def get(self, request, *args, **kwargs):
        context = self.context()
        context['dumpform'] = forms.DumpUploadForm()
        return self.render('config/projects.html', context)

    def post(self, request, *args, **kwargs):
        context = self.context()
        context['dumpform'] = form = forms.DumpUploadForm(request.POST, request.FILES)
        if form.is_valid():
            self.upload_backup(form.cleaned_data)
            return HttpResponseRedirect(reverse('web:admin-projects'))

        messages.error(request, _(u"Erroneous data, probably because you forgot to specify a file."))
        return self.render('config/projects.html', context)

    def upload_backup(self, data):
        try:
            zfile = zipfile.ZipFile(data['dumpfile'], 'r')
        except zipfile.BadZipfile:
            messages.error(self.request, _(u"The zip file must be a valid."))
            return

        zfile_names = zfile.namelist()
        print zfile_names

        big_map = {'users':{}}
        users = zfile.read('user.json')

        for user in serializers.deserialize('json', users):
            qs = models.User.objects.filter(username=user.object.username)
            if len(qs) == 0:
                old_id = user.object.id
                user.object.set_unusable_password()
                user.object.id = None
                user.save()
                big_map['users'][old_id] = user.object.id

            else:
                qsuser = qs[0]
                big_map['users'][user.object.id] = qs[0].id
        
        # fix project json
        projects = zfile.read('project.json')
        pdata = json.loads(projects)
        for x in xrange(len(pdata)):
            current_owner = pdata[x]['fields']['owner']
            if current_owner in big_map['users']:
                pdata[x]['fields']['owner'] = big_map['users'][current_owner]

        projects = json.dumps(pdata)

        projects = list(serializers.deserialize('json', projects))
        if len(projects) > 1 or len(projects) < 1:
            messages.error(self.request, _(u"Backup invalid"))
            return

        project = projects[0]
        if models.Project.objects.filter(slug=project.object.slug).exists():
            messages.error(self.request, _(u"The project already exists, aborted."))
            return
        
        project.object.id = None
        project.save()

        from pprint import pprint
        pprint(big_map)

        user_roles = zfile.read('user_role.json')

        #fix user_role
        urdata = json.loads(user_roles)
        for x in xrange(len(urdata)):
            current_user = urdata[x]['fields']['user']
            if current_user in big_map['users']:
                urdata[x]['fields']['user'] = big_map['users'][current_user]

        user_roles = json.dumps(urdata)
        for ur in serializers.deserialize('json', user_roles):
            ur.object.id = None
            ur.save()


        milestones = zfile.read('milestones.json')
        big_map['mls'] = {}

        for ml in serializers.deserialize('json', milestones):
            old_id = ml.object.id
            ml.object.id = None
            ml.save()
            big_map['mls'][old_id] = ml.object.id

        pprint(big_map)

        userstories = zfile.read('us.json')

        # fix user_stories json
        udata = json.loads(userstories)
        for x in xrange(len(udata)):
            current_ownerid = udata[x]['fields']['owner']
            if current_ownerid in big_map['users']:
                udata[x]['fields']['owner'] = big_map['users'][current_ownerid]

        big_map['us'] = {}
        userstories = json.dumps(udata)
        for us in serializers.deserialize('json', userstories):
            old_id = us.object.id
            us.object.id = None
            us.save()
            big_map['us'][old_id] = us.object.id

        tasks = zfile.read('tasks.json')

        # fix tasks json
        tdata = json.loads(tasks)
        for x in xrange(len(tdata)):
            cur_assignedto = tdata[x]['fields']['assigned_to']
            cur_owner = tdata[x]['fields']['owner']
            cur_us = tdata[x]['fields']['user_story']

            if cur_assignedto and cur_assignedto in big_map['users']:
                tdata[x]['fields']['assigned_to'] = \
                    big_map['users'][cur_assignedto]

            if cur_owner in big_map['users']:
                tdata[x]['fields']['owner'] = big_map['users'][cur_owner]

            if cur_us and cur_us in big_map['us']:
                tdata[x]['fields']['user_story'] = big_map['us'][cur_us]

        big_map['tsk'] = {}
        tasks = json.dumps(tdata)
        for task in serializers.deserialize('json', tasks):
            old_id = task.object.id
            task.object.id = None
            task.save()
            big_map['tsk'][old_id] = task.object.id

        messages.info(self.request, _(u"Backup successfully restored."))
    
    @login_required
    def dispatch(self, *args, **kwargs):
        return super(AdminProjectsView, self).dispatch(*args, **kwargs)



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
