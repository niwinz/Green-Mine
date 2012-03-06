# -*- coding: utf-8 -*- 

from django.core.urlresolvers import reverse
from django.core.mail import EmailMessage
from django.conf import settings
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import Promise
from django.utils.encoding import force_unicode
from django.template.loader import render_to_string
from django.template import RequestContext, loader


import datetime, hashlib, os.path, os
import random, string, uuid
import unicodedata


class Singleton(type):
    """ Singleton metaclass. """
    def __init__(cls, name, bases, dct):
        cls.__instance = None
        type.__init__(cls, name, bases, dct)
 
    def __call__(cls, *args, **kw):
        if cls.__instance is None:
            cls.__instance = type.__call__(cls, *args,**kw)
        return cls.__instance


def clear_model_dict(data):
    hidden_fields = ['password']

    new_dict = {}
    for key, val in data.items():
        if not key.startswith('_') and key not in hidden_fields:
            new_dict[key] = val

    return new_dict


def normalize_tagname(tagname):
    value = unicodedata.normalize('NFKD', tagname).encode('ascii', 'ignore')
    return value.lower()


def set_token(user):
    """
    Set new token for user profile.
    """

    token = unicode(uuid.uuid4())
    profile = user.get_profile()
    profile.token = token
    profile.save()
    
    return token


def send_recovery_email(user):
    """
    Set token for user profile and send password
    recovery mail.
    """

    context = {
        'user': user, 
        'token': set_token(user),
        'current_host': settings.HOST,
    }
    email_body = loader.render_to_string("email/forgot.password.html", 
                                                                context)
    email_message = EmailMessage(
        body = email_body,
        to = [user.email],
        subject = _(u'Greenmine: password recovery.'),
    )
    email_message.content_subtype = "html"
    email_message.send(fail_silently=True)
