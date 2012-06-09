# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib import messages
from urlparse import urlparse

from . import version

def main(request):
    context_extra = dict(
        user = request.user,
        debug = settings.DEBUG,
        current_url = request.META.get('PATH_INFO'),
        previous_url = request.META.get("HTTP_REFERER", u"/"),
        current_host = settings.HOST,
    )
    
    # Put main_title into context
    tmp_main_title = 'Greenmine'
    context_extra['MAIN_TITLE'] = tmp_main_title

    # Make current_url manually
    context_extra['full_current_url'] = context_extra['current_url']
    if request.META.get("QUERY_STRING"):
        context_extra['full_current_url'] += "?%s" % (request.META.get("QUERY_STRING"))

    context_extra['version'] = version.version_as_string()

    return context_extra
