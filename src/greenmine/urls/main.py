# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from greenmine.views import main, config

urlpatterns = patterns('',
    url(r'^$', main.ProjectsView.as_view(), name='projects'),
    url(r'^login/$', main.LoginView.as_view(), name='login'),
    url(r'^config/profile/$', config.ProfileView.as_view(), name='profile'),
    url(r'^config/projects/$', config.AdminProjectsView.as_view(), name='admin-projects'),
    url(r'^config/projects/(?P<pslug>[\w\d\-]+)/export/$',
        config.AdminProjectExport.as_view(), name="admin-project-export"),
    url(r'^project/create/$', main.ProjectCreateView.as_view(), name='project-create'),
    url(r'^(?P<slug>[\w\d\-]+)/dashboard/$', main.ProjectView.as_view(), name='project'),

    url(r'^media/', include('django_dbstorage.urls'))
)


