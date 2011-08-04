# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from greenmine.views.main import ProjectsView, ProjectView, LoginView 
from greenmine.views.config import ProfileView

urlpatterns = patterns('',
    url(r'^$', ProjectsView.as_view(), name='projects-show'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url('^config/profile/$', ProfileView.as_view(), name='profile-show'),
    url(r'^(?P<projectid>[\w\-]+)/$', ProjectView.as_view(), name='project-show'),
)


