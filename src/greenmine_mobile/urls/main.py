# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from greenmine_mobile import views
from django.conf import settings


js_info_dict = {
    'packages': ('greenmine_mobile',),
}

urlpatterns = patterns('',
    url(r'^$', views.ProjectsView.as_view(), name='projects'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    #url(r'^config/profile/$', config.ProfileView.as_view(), name='profile'),
    #url(r'^config/projects/$', config.AdminProjectsView.as_view(), name='admin-projects'),
    #url(r'^config/projects/(?P<pslug>[\w\d\-]+)/export/$',
    #    config.AdminProjectExport.as_view(), name="admin-project-export"),
    #url(r'^project/create/$', main.ProjectCreateView.as_view(), name='project-create'),
    url(r'^(?P<pslug>[\w\d\-]+)/dashboard/$', views.ProjectView.as_view(), name='project'),
    url(r'^(?P<pslug>[\w\d\-]+)/milestone/(?P<mid>\d+)/issues/$',
        views.ProjectIssuesView.as_view(), name='project-issues-view'),
    url(r'^(?P<pslug>[\w\d\-]+)/issue/(?P<iref>[\w\d]+)/$', views.IssueView.as_view(), name='issue'),
)

urlpatterns += patterns('',
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict, name='jsi18n'),
)
