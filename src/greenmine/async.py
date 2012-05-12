# -*- coding: utf-8 -*-

import logging

from greenqueue.core import Library
register = Library()

from django.template import loader
from greenmine.utils import mail, set_token

@register.task(name='mail-user.story-create')
def mail_user_story_create(host, subject, users):
    context = {
        'current_host': host,
    }

    param = {'subject': subject}

    for user in users:
        params.update({'to': [user.email]})
        mail.send("user.story.created", context, **params)

@register.task(name='mail-new.registration')
def mail_new_registration(host, subject, user):
    context = {
        'user': user,
        'token': set_token(user),
        'current_host': host,
    }

    params = {
        'to': [user.email],
        'subject': subject,
    }

    return mail.send("new.registration", context, **params)

@register.task(name='mail-recovery.password')
def mail_recovery_password(host, subject, user):
    """
    Set token for user profile and send password
    recovery mail.
    """

    context = {
        'user': user,
        'token': set_token(user),
        'current_host': host,
    }

    params = {
        'to': [user.email],
        'subject': subject,
    }

    return mail.send("password.recovery", context, **params)
