# -*- coding: utf-8 -*-

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


import logging
logger = logging.getLogger('greenmine')

import copy

from django.views.generic import (
    TemplateView, 
    RedirectView, 
    DetailView, 
    FormView, 
    CreateView, 
    UpdateView, 
    DeleteView, 
    ListView,
    View
)

from greenmine.models import *
from greenmine.utils import *


class ApiView(View):
    def render_to_response(self, context):
        if isinstance(context, dict):
            response_data = simplejson.dumps(context, cls=LazyEncoder, indent=4, sort_keys=True)
        else:
            response_data = context
        return HttpResponse(response_data, mimetype='text/plain')

    def render_to_error(self, context):
        response_dict = {'valid': False, 'errors':[]}
        if isinstance(context, (str, unicode)):
            response_dict['errors'].append(context)
        elif isinstance(context, (list,tuple)):
            response_dict['errors'] = context

        return self.render_to_response(response_dict)

    def render_to_ok(self, context):
        response = {'valid': True, 'errors': []}
        response.update(context)
        return self.render_to_response(response)


class RestrictedApiView(ApiView):
    @method_decorator(api_login_required)
    def dispatch(self, *args, **kwargs):
        return super(RestrictedApiView, self).dispatch(*args, **kwargs)


class ApiLogin(ApiView):
    def post(self, request):
        if "username" not in request.POST or "password" not in request.POST:
            return self.render_to_error([_(u'Debe especificar las credenciales para poder autenticarse')])
        else:
            try:
                userobj = User.objects.get(username=request.POST['username'], password=encrypt_password(request.POST['password']))
                request.session['current_user_id'] = userobj.id
            except User.DoesNotExist:
                return self.render_to_error([_(u'Usuario o contraseña son incorrectos')])

            return self.render_to_ok({'id': userobj.id})


class ApiUserView(RestrictedApiView):
    def get(self, request):
        context = copy.deepcopy(self.standard_response)

        if "id" in request.GET:
            qparams = {'pk': request.GET['id']}
        elif "username" in request.GET:
            qparams = {'username': request.GET['username']}
        else:
            qparams = {'username': request.current_user.username }

        try:
            userobj = User.objects.get(**qparams)
            context['object'] = clear_model_dict(userobj.__dict__)
            context['id'] = userobj.id
        except User.DoesNotExist:
            context['errors'].append(_(u'El usuario solicitado no existe.'))

        return self.render_to_response(context)


class ApiUserEdit(RestrictedApiView):
    def post(self, request):
        context = copy.deepcopy(self.standard_response)
        userobj = request.user

        if 'description' in request.POST:
            userobj.description = request.POST.get('description')

        if 'email' in request.POST:
            userobj.email = request.POST.get('email')

        if 'name' in request.POST:
            userobj.name = request.POST.get('name')

        if 'superuser' in request.POST and request.user.is_superuser():
            opt = request.POST.get('superuser')
            if opt in ['0','1']:
                userobj.superuser = bool(int(opt))

        if 'password' in request.POST:
            userobj.password = encrypt_password(request.POST.get('password'))

        # file process
        if "photo" in request.FILES:
            userobj.photo = request.FILES['photo']

        userobj.save()
        context['id'] = userobj.id
        
        return self.render_to_response(context)


class ApiUserAdd(RestrictedApiView):
    def post(self, request, *args, **kwargs):
        context = copy.deepcopy(self.standard_response)

        if 'username' not in request.POST:
            context['errors'].append(force_unicode(_(u'El parametro username es obligatorio')))
            return self.render_to_response(context)
        
        email = request.POST.get('email', '')
        name = request.POST.get('name', '')
        send_rnd_password = request.POST.get('send_rnd_password', False)
        project = request.POST.get('project', '')
        role = request.POST.get('role', 'developer')
        superuser = request.POST.get('superuser', False)

        # check if user exists.
        try:
            userobj = User.objects.get(username=username)
            userobj.modified_date = datetime.datetime.now()
            context['id'] = userobj.id
            if "project" not in request.POST:
                context['errors'].append(force_unicode(_(u'Ya existe un usuario con este nombre')))
                return self.render_to_response(context)

        except User.DoesNotExist:
            userobj = User.objects.create(username=username, email=email)
            if superuser and request.user.is_superuser():
                userobj.superuser = True

            if "description" in request.POST:
                userobj.description = request.POST.get('description')
            
            userobj.save()
            context['id'] = userobj.id

        from greenmine.models import ROLE_CHOICES

        if project:
            if not Project.objects.filter(name=project).exists():
                context['errors'].append(force_unicode(_(u'El proyecto %s no existe.' % (project))))
            else:
                if role not in dict(ROLE_CHOICES).keys():
                    context['errors'].append(force_unicode(_(u'Role invalido')))
                else:
                    try:
                        obj = ProjectUser.objects.create(
                            project = Project.objects.get(name=project),
                            user = userobj
                        )
                    except IntegrityError:
                        context['errors'].append(force_unicode(_(u'Ya existe este usuario en el proyecto')))
                    
        return self.render_to_response(context)


class ApiCreateProject(RestrictedApiView):
    def post(self, request):
        context = copy.deepcopy(self.standard_response)
        
        if "name" not in request.POST:
            context['errors'].append(_(u'El parametro %s es obligatorio' % ('name')))
            return self.render_to_response(context)
        elif Project.objects.filter(name=request.POST['name']).exists():
            context['errors'].append(_(u'El proyecto con el nombre especificado ya existe.'))
            return self.render_to_response(context)

        if "role" not in request.POST and not request.user.is_superuser():
            context['errors'].append(_(u'El parametro %s es obligatorio' % ('role')))
            return self.render_to_response(context)

        from greenmine.models import PROJECT_TYPE_CHOICES
        if "type" in request.POST:
            if request.POST['type'] not in dict(PROJECT_TYPE_CHOICES).keys():
                context['errors'].append(_(u"El tipo de proyecto elejido es invalido."))
                return self.render_to_response(context)

        from greenmine.models import ROLE_CHOICES
        role = request.POST.get('role', None)
        if role and not role in dict(ROLE_CHOICES).keys():
            context['errors'].append(force_unicode(_(u'Role invalido')))
            return self.render_to_response(context)
        else:
            role = 'developer'
        
        try:
            project = Project.objects.create(
                name = request.POST['name'],
                owner = request.user,
                type = 'standatd' if "type" not in request.POST else request.POST['type'],
                desc = request.POST.get('desc', ''),
                public = False
            )
            context['valid'] = True
            context['id'] = project.id
            context['project'] = clear_model_dict(project.__dict__)

            if not request.user.is_superuser():
                project_user = ProjectUser.objects.create(
                    user = request.user,
                    project = project,
                    role = role )

        except IntegrityError:
            context['errors'].append(_(u"No se ha podido crear el proyecto"))

        return self.render_to_response(context)

        


