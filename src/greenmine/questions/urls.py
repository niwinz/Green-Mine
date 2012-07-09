# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url

from .views import *

urlpatterns = patterns('',
    url(r'^$', QuestionsListView.as_view(), name='questions'),
    url(r'^create/$', QuestionsCreateView.as_view(), name='questions-create'),
    url(r'^(?P<qslug>[\w\d\-]+)/view/$', QuestionsView.as_view(), name='questions-view'),
    url(r'^(?P<qslug>[\w\d\-]+)/edit/$', QuestionsEditView.as_view(), name='questions-edit'),
    url(r'^(?P<qslug>[\w\d\-]+)/delete/$', QuestionsDeleteView.as_view(), name='questions-delete'),
)
