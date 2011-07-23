# -*- coding: utf-8 -*-

from django.views.decorators.cache import cache_page
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect, HttpResponse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, loader
from django.contrib import messages

import logging
logger = logging.getLogger('greenmine')

from django.views.generic import (
    TemplateView, 
    RedirectView, 
    DetailView, 
    FormView, 
    CreateView, 
    UpdateView, 
    DeleteView, 
    ListView
)

class GenericResponseMixIn(object):
    template_name = None
    redirect_on_post_next = False
    redirect_on_get_next = False

    def render_to_response(self, context, **response_kwargs):
        if self.redirect_on_post_next and self.request.method == 'POST':
            if "next" in self.request.GET:
                return HttpResponseRedirect(self.request.GET['next'])

        if self.redirect_on_get_next and self.request.method == 'GET':
            if "next" in self.request.GET:
                return HttpResponseRedirect(self.request.GET['next'])

        return render_to_response(self.get_template_names(), context,
            context_instance = RequestContext(self.request), **response_kwargs)


class HomeView(GenericResponseMixIn, TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        if not request.current_user.is_authenticated():
            return HttpResponseRedirect(reverse('login'))

        return super(HomeView, self).get(request, *args, **kwargs)


from greenmine.forms import LoginForm
from greenmine.models import User
from greenmine.utils import encrypt_password

class LoginView(GenericResponseMixIn, TemplateView):
    template_name = 'login.html'
    redirect_on_post_next = True

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['form'] = LoginForm()
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            request.session['current_user_id'] = form._user.id
            
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)
