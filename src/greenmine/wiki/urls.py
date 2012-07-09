# -*- coding: utf-8 -*-

from __future__ import absolute_import
from django.conf.urls.defaults import patterns, include, url

from .views import *

urlpatterns = patterns('',
    url(r'^(?P<wslug>[\d\w\-]+)/view/$', WikiPageView.as_view(), name='wiki-page'),
    url(r'^(?P<wslug>[\d\w\-]+)/view/history/$', WikiPageHistoryView.as_view(), name='wiki-page-history'),
    url(r'^(?P<wslug>[\d\w\-]+)/view/history/(?P<hpk>\d+)/$',
        WikiPageHistoryView.as_view(), name='wiki-page-history-view'),

    url(r'^(?P<wslug>[\d\w\-]+)/edit/$', WikiPageEditView.as_view(), name='wiki-page-edit'),
    url(r'^(?P<wslug>[\d\w\-]+)/delete/$', WikipageDeleteView.as_view(), name='wiki-page-delete'),
)
