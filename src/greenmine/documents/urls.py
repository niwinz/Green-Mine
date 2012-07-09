# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from .views import *

urlpatterns = patterns('',
    url(r'^$', Documents.as_view(), name='documents'),
    url(r'^(?P<docid>\d+)/delete/$', DocumentsDelete.as_view(), name='documents-delete'),
)
