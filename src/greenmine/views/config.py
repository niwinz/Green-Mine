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

        messages.error(request, _(u"Datos erroneos, seguramente por que se le olvido especificar un fichero."))
        return self.render('config/projects.html', context)

    def upload_backup(self, data):
        try:
            zfile = zipfile.ZipFile(data['dumpfile'], 'r')
        except zipfile.BadZipfile:
            messages.error(self.request, _(u"El archivo debe ser un zip valido."))
            return

        zfile_names = zfile.namelist()
        print zfile_names
        if "project.json" not in zfile_names or "milestones.json" not in zfile_names:
            messages.error(self.request, _(u"El archivo que ha subido no es un backup valido."))
            return

        project_data = zfile.read('project.json')
        milestone_data = zfile.read('milestones.json')
        
        projects = list(serializers.deserialize('json', project_data))
        if len(projects) > 1 or len(projects) < 1:
            messages.error(self.request, _(u"Backup invalido"))
            return
        
        project = projects[0]
        if models.Project.objects.filter(slug=project.object.slug).exists():
            messages.error(self.request, _(u"El proyecto ya existe, abortado."))
            return
        
        project.object.id = None
        project.save()

        for ml in serializers.deserialize('json', milestone_data):
            ml.object.id = None
            ml.save()

        messages.info(self.request, _(u"Backup restaurado con exito."))
    
    @login_required
    def dispatch(self, *args, **kwargs):
        return super(AdminProjectsView, self).dispatch(*args, **kwargs)



class AdminProjectExport(GenericView):
    def get(self, request, pslug):
        project = get_object_or_404(models.Project, slug=pslug)
        
        tmpfile = StringIO()
        zfile = zipfile.ZipFile(tmpfile, 'a')
        project_data = serializers.serialize("json", [project])
        milestones_data = serializers.serialize("json", project.milestones.all())
        zfile.writestr('project.json', project_data)
        zfile.writestr('milestones.json', milestones_data)
        zfile.close()

        response = HttpResponse(tmpfile.getvalue(), mimetype='application/zip')
        tmpfile.close()
        response['Content-Disposition'] = 'attachment; filename=%s-backup.zip' % (project.slug)
        return response


class ProfileView(GenericView):
    template_name = 'config/profile.html'

    def get(self, request):
        form = forms.ProfileForm(instance=request.user)
        context = {'form':form, 'csel':'profile'}
        return self.render(self.template_name, context)

    def post(self, request):
        form = forms.ProfileForm(request.POST, request.FILES, instance=request.user)
        context = {'form':form, 'csel':'profile'}

        if not form.is_valid():
            return self.render(self.template_name, context)

        sem = transaction.savepoint()
        try:
            request.user = form.save()
        except IntegrityError as e:
            transaction.savepoint_rollback(sem)
            
            messages.error(request, _(u'Integrity error: %(e)s') % {'e':unicode(e)})
            return self.render(self.template_name, context)
        
        transaction.savepoint_commit(sem)

        messages.info(request, _(u'Profile save success!'))
        return HttpResponseRedirect(reverse('web:profile'))

    @login_required
    def dispatch(self, *args, **kwargs):
        return super(ProfileView, self).dispatch(*args, **kwargs)

