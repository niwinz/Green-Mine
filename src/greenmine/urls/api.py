# -*- coding: utf-8 -*- 
from django.conf.urls.defaults import patterns, include, url

from greenmine.views import api

urlpatterns = patterns('',
    url(r'^login$', api.ApiLogin.as_view(), name='login'),
    url(r'^user/list/$', api.UserListApiView.as_view(), name='user-list'),
    
    url(r'^project/(?P<pslug>[\w\d\-]+)/milestones/$',
        api.MilestonesForProjectApiView.as_view(), name='milestones-for-project'),

    url(r'^project/(?P<pslug>[\w\d\-]+)/m/(?P<mid>\d+)/tasks/$', 
        api.TasksForMilestoneApiView.as_view(), name="tasks-for-milestone"),
    url(r'^project/(?P<pslug>[\w\d\-]+)/tasks/$',
        api.TasksForMilestoneApiView.as_view(), name="unasigned-tasks-for-poject"),
    url(r'^project/(?P<pslug>[\w\d\-]+)/delete/$', 
        api.ProjectDeleteApiView.as_view(), name="project-delete"),
    url(r'^project/(?P<pslug>[\w\d\-]+)/milestone/create/$',
        api.MilestoneCreateApiView.as_view(), name="project-milestone-create"),
    url(r'^project/(?P<pslug>[\w\d\-]+)/milestone/(?P<mid>\d+)/edit/$',
        api.MilestoneEditApiView.as_view(), name="project-milestone-edit"),
    url(r'^project/(?P<pslug>[\w\d\-]+)/issue/create/$',
        api.IssueCreateApiView.as_view(), name="project-issue-create"),
    url(r'^project/(?P<pslug>[\w\d\-]+)/issue/(?P<issueid>\d+)/edit/$',
        api.IssueEditApiView.as_view(), name="issue-edit"),
    url(r'^i18n/lang/$', api.I18NLangChangeApiView.as_view(), 
        name='i18n-setlang'),
    url(r'^password/forgotten/$', 
        api.ForgottenPasswordApiView.as_view(), name='password-forgotten'),
)

