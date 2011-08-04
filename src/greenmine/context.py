# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib import messages
from urlparse import urlparse

from .models import GSettings

def main(request):
    context_extra = dict(
        debug = settings.DEBUG,
        current_url = request.META.get('PATH_INFO'),
        previous_url = request.META.get("HTTP_REFERER", u"/"),
    )
    
    # Put main_title into context
    try:
        tmp_main_title = GSettings.objects.get(key='core.maintitle')
    except GSettings.DoesNotExist:
        tmp_main_title = 'Greenmine Temporal Title'
    finally:
        context_extra['MAIN_TITLE'] = tmp_main_title

    # Make current_url manually
    context_extra['full_current_url'] = context_extra['current_url']
    if request.META.get("QUERY_STRING"):
        context_extra['full_current_url'] += "?%s" % (request.META.get("QUERY_STRING"))
    return context_extra
