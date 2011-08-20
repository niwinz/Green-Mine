# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from greenmine.views.main import ProjectsView, ProjectView, LoginView 
from greenmine.views.config import ProfileView, ProjectCreateView

urlpatterns = patterns('',
    url(r'^$', ProjectsView.as_view(), name='projects'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^config/profile/$', ProfileView.as_view(), name='profile'),
    url(r'^config/project/create/$', ProjectCreateView.as_view(), name='project-create'),
    url(r'^(?P<slug>[\w\d\-]+)/dashboard/$', ProjectView.as_view(), name='project'),
    url(r'^media/', include('django_dbstorage.urls'))
)


