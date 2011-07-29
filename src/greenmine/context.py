# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib import messages
from urlparse import urlparse

def main(request):
    context_extra = dict(
        debug = settings.DEBUG,
        previous_url = request.META.get("HTTP_REFERER", u"/"),
    )
    
    context_extra['MAIN_TITLE'] = settings.MAIN_TITLE
    # Make current_url manually
    context_extra['current_url'] = request.META.get('PATH_INFO')
    context_extra['full_current_url'] = context_extra['current_url']
    if request.META.get("QUERY_STRING"):
        context_extra['full_current_url'] += "?%s" % (request.META.get("QUERY_STRING"))

    #context_extra['full_current_url'] = context_extra['BASE_HOST'] + context_extra['current_url']
    return context_extra
