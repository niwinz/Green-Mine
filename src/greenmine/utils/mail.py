# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils.translation import ugettext
from django.utils.encoding import force_unicode
from django.template import RequestContext, loader

from . import Singleton, set_token


MAILS = {
    'new.registration': 'email/new.user.html',
    'password.recovery': 'email/forgot.password.html',
    'user.story.created': 'email/user.story.created.html',
}


def send_user_story_create_mail(users):
    context = {
        'current_host': settings.HOST,
    }

    params = {'subject': ugettext(u"Greenmine: new user story!")}

    for user in users:
        params.update({'to': [user.email]})
        send("user.story.created", context, **params)
        

def send_new_registration_mail(user):
    context = {
        'user': user, 
        'token': set_token(user),
        'current_host': settings.HOST,
    }

    params = {
        "to": [user.email],
        "subject": ugettext("Greenmine: Welcome!"),
    }

    return send("new.registration", context, **params)


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

    params = {
        "to": [user.email],
        "subject": ugettext("Greenmine: password recovery."),
    }
    return send("password.recovery", context, **params)


def send(key, context, **kwargs):
    if key not in MAILS:
        raise ValueError("Invalid key parameter")

    template = loader.render_to_string(MAILS[key], context)
    return send_email(template, **kwargs)


def send_email(body, to, subject, content_subtype='html'):
    if not isinstance(to, (list,tuple)):
        to = [to]

    email_message = EmailMessage(
        body = body,
        to = to,
        subject = subject
    )
    email_message.content_subtype = content_subtype
    email_message.send(fail_silently=False)
