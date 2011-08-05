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

from ..forms import ProfileForm
from ..models import User
from ..utils import encrypt_password

class ProfileView(GenericView):
    template_name = 'config/profile.html'

    def get(self, request):
        form = ProfileForm(instance=request.user)
        context = {'form':form}
        return self.render(self.template_name, context)

    def post(self, request):
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            sem = transaction.savepoint()
            try:
                request.user = form.save()
                transaction.savepoint_commit(sem)
            except IntegrityError as e:
                transaction.savepoint_rollback(sem)
                messages.error(request, _(u'Integrity error: %(error)') % (unicode(e)))
                return self.render(self.template_name)
            
            messages.info(request, _(u'Profile save success!'))
            return HttpResponseRedirect(reverse('web:profile-show'))


                
            

    @login_required
    def dispatch(self, *args, **kwargs):
        return super(ProfileView, self).dispatch(*args, **kwargs)
