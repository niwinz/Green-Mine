# -*- coding: utf-8 -*- 
from django.conf.urls.defaults import patterns, include, url

from greenmine.views import api

urlpatterns = patterns('',
    url(r'^login$', api.ApiLogin.as_view(), name='login'),
    url(r'^user/list/$', api.UserListApiView.as_view(), name='user-list'),

    url(r'^project/(?P<pslug>[\w\d\-]+)/m/(?P<mid>\d+)/tasks/$', 
        api.TasksForMilestoneApiView.as_view(), name="tasks-for-milestone"),
    url(r'^project/(?P<pslug>[\w\d\-]+)/tasks/$',
        api.TasksForMilestoneApiView.as_view(), name="unasigned-tasks-for-poject"),
    url(r'^project/(?P<pslug>[\w\d\-]+)/delete/$', 
        api.ProjectDeleteApiView.as_view(), name="project-delete"),
    url(r'^project/(?P<pslug>[\w\d\-]+)/milestone/create/$',
        api.MilestoneCreateApiView.as_view(), name="project-milestone-create"),
)

