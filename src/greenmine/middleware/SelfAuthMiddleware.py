# -*- coding: utf-8 -*-

from django.db import IntegrityError
from django.conf import settings
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.conf import settings

from greenmine.models import User
from greenmine.utils import encrypt_password

import re

class AnonUser(object):
    def is_authenticated(self):
        return False

    def is_superuser(self):
        return False


class SelfAuthMiddleware(object):
    def process_request(self, request):
        """
        User agent processor to determine whether the incoming
        user is someone using a browser, or a mercurial client.
        """
        
        agent = re.compile(r'^(mercurial).*')
        accept = request.META.get('HTTP_ACCEPT', None)
        result = agent.match(request.META.get('HTTP_USER_AGENT', ""))
        
        # mercurial request test.
        if result and accept.startswith('application/mercurial-'):
            request.is_mercurial = True
        else:
            request.is_mercurial = False

        if "current_user_id" in request.session:
            request.user = User.objects.get(pk=request.session['current_user_id'])

        else:
            auth_string = request.META.get('HTTP_AUTHORIZATION')
            
            if auth_string is None or not auth_string.startswith("Basic"):
                request.current_user = AnonUser()
                return None

            _, basic_hash = auth_string.split(' ', 1)
            username, password = basic_hash.decode('base64').split(':', 1)
            try:
                user = User.objects.get(username=username, password=encrypt_password(password))
            except User.DoesNotExist:
                request.user = AnonUser()
            
            return None
