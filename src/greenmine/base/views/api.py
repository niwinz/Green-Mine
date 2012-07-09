# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils.decorators import method_decorator
from django.db.models import Q

from django_gravatar.helpers import get_gravatar_url, has_gravatar

# Temporal imports
from greenmine.base.models import *
from greenmine.scrum.models import *

from greenmine.core.decorators import login_required
from greenmine.core.generic import GenericView

import logging, re
logger = logging.getLogger('greenmine')


class UserListApiView(GenericView):
    """
    Autocomplete helper for project create/edit.
    This autocompletes and searches users by term.
    """

    @login_required
    def get(self, request):
        if "term" not in request.GET:
            return self.render_to_ok({'list':[]})

        term = request.GET['term']
        users = User.objects.filter(
            Q(username__istartswith=term) | Q(first_name__istartswith=term) | Q(last_name__istartswith=term)
        )
        users_list = []

        for user in users:
            users_list_item = {'id': user.id}

            full_name = user.get_full_name()
            if full_name:
                users_list_item['label'] = full_name
                users_list_item['value'] = full_name
            else:
                users_list_item['label'] = user.username
                users_list_item['value'] = user.username

            if user.get_profile().photo:
                users_list_item['gravatar'] = user.get_profile().photo.url
            else:
                users_list_item['gravatar'] = get_gravatar_url(user.email, size=30)

            users_list.append(users_list_item)

        context = {'list': users_list}
        return self.render_to_ok(context)


class I18NLangChangeApiView(GenericView):
    """
    View for set language.
    """

    def get(self, request):
        if 'lang' in request.GET and request.GET['lang'] \
                                    in dict(settings.LANGUAGES).keys():
            request.session['django_language'] = request.GET['lang']
            if request.META.get('HTTP_REFERER', ''):
                return self.render_redirect(request.META['HTTP_REFERER'])
            elif "next" in request.GET and request.GET['next']:
                return self.render_redirect(request.GET['next'])

        return self.render_redirect('/')
