# -*- coding: utf-8 -*-

import logging

from greenqueue.core import Library
register = Library()

from django.template import loader
from greenmine.utils import mail, set_token
from django.utils import translation


@register.task(name='send-mail')
def send_mail(subject, body, to)
    email_message = EmailMessage(body=body, subject=subject, to=to)
    email_message.send()


@register.task(name='mail-question.assigned')
def mail_question_assigned(host, subject, question):
    context = {
        'user': question.assigned_to,
        'current_host': host,
        'question': question,
    }

    params = {
        'to': [question.assigned_to.email],
        'subject': subject,
    }
    return mail.send("question.assigned", context, **params)

@register.task(name='mail-question.created')
def mail_question_created(host, subject, question):
    participants = set(question.project.participants.all())

    context = {
        'question': question,
        'current_host': host,
        'project': question.project,
    }

    params = {
        'to': [x.email for x in participants],
        'subject': subject,
    }

    return mail.send("question.created", context, **params)
