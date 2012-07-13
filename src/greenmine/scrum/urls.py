# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

from .views import tasks
from .views import issues
from .views import main
from .views import backlog
from .views import dashboard
from .views import userstory
from .views import project
from .views import milestone

tasks_patterns = patterns('',
    url(r'^create/$', tasks.CreateTask.as_view(), name='tasks-create'),
    url(r'^(?P<tref>[\w\d]+)/view/$', tasks.TaskView.as_view(), name='tasks-view'),
    url(r'^(?P<tref>[\w\d]+)/delete/$', tasks.TaskDelete.as_view(), name='tasks-delete'),
    url(r'^(?P<tref>[\w\d]+)/send/comment/$', tasks.TaskSendComment.as_view(), name='tasks-send-comment'),
)

issues_patterns = patterns('',
    url(r'^$', issues.IssueList.as_view(), name='issues-list'),
    url(r'^create/$', issues.CreateIssue.as_view(), name='issues-create'),
    url(r'^(?P<tref>[\w\d]+)/view/$', issues.IssueView.as_view(), name='issues-view'),
    url(r'^(?P<tref>[\w\d]+)/edit/$', issues.EditIssue.as_view(), name='issues-edit'),
    url(r'^(?P<tref>[\w\d]+)/send/comment/$', issues.IssueSendComment.as_view(), name='issues-send-comment'),
)

backlog_patterns = patterns('',
    url(r'^$', backlog.BacklogView.as_view(), name='project-backlog'),
    url(r'^stats/$', backlog.BacklogStats.as_view(), name='project-backlog-stats'),
    url(r'^left-block/$', backlog.BacklogLeftBlockView.as_view(), name='project-backlog-left-block'),
    url(r'^right-block/$', backlog.BacklogRightBlockView.as_view(), name='project-backlog-right-block'),
    url(r'^burndown/$', backlog.BacklogBurnDownView.as_view(), name='project-backlog-burndown'),
    url(r'^burnup/$', backlog.BacklogBurnUpView.as_view(), name='project-backlog-burnup'),
)

dashboard_patterns = patterns('',
    url(r'^$',dashboard.DashboardView.as_view(), name="dashboard"),
    url(r'^(?P<mid>(?:\d+))/$', dashboard.DashboardView.as_view(), name="dashboard"),
    url(r'^(?P<mid>(?:\d+))/burndown/$',
        dashboard.MilestoneBurndownView.as_view(), name="milestone-burndown"),
    url(r'^api/$', dashboard.DashboardApiView.as_view(), name="dashboard-api"),
    url(r'^api/crate-task/$', dashboard.DashboardCreateTask.as_view(), name="dashboard-api-create-task"),
)

milestone_patterns = patterns('',
    url(r'^create/$', milestone.MilestoneCreateView.as_view(), name='milestone-create'),
    url(r'^(?P<mid>\d+)/edit/$', milestone.MilestoneEditView.as_view(), name='milestone-edit'),
    url(r'^(?P<mid>\d+)/delete/$', milestone.MilestoneDeleteView.as_view(), name='milestone-delete'),
)

userstories_patterns = patterns('',
    # User storys
    url(r'^create/$', userstory.UserStoryCreateView.as_view(), name='user-story-create'),
    url(r'^(?P<iref>[\d\w]+)/edit/$', userstory.UserStoryEdit.as_view(), name='user-story-edit'),
    url(r'^(?P<iref>[\d\w]+)/edit-inline/$', userstory.UsFormInline.as_view(), name='user-story-edit-inline'),
    url(r'^(?P<iref>[\d\w]+)/delete/$', userstory.UserStoryDeleteView.as_view(), name='user-story-delete'),
    url(r'^(?P<iref>[\w\d]+)/view/$', userstory.UserStoryView.as_view(), name='user-story'),

    # API
    url(r'^(?P<iref>[\d\w]+)/unassign/$', userstory.UnassignUserStory.as_view(), name="unassign-us"),
    url(r'^(?P<iref>[\d\w]+)/assign/$', userstory.AssignUserStory.as_view(), name="assign-us"),
)

urlpatterns = patterns('',
    url(r'^create/$', project.ProjectCreateView.as_view(), name='project-create'),
    url(r'^(?P<pslug>[\w\d\-]+)/delete/$', project.ProjectDelete.as_view(), name='project-delete'),

    # settings and admin
    url(r'^personal-settings/$',  project.ProjectUserSettings.as_view(), name="project-personal"),
    url(r'^personal-settings/(?P<pslug>[\w\d\-]+)/$',
        project.ProjectUserSettingsIndividual.as_view(), name="project-personal-individual"),
    url(r"^(?P<pslug>[\w\d\-]+)/admin/$", project.ProjectAdminSettings.as_view(), name="project-admin"),


    #url(r'^(?P<pslug>[\w\d\-]+)/task/(?P<tref>[\w\d]+)/edit/$',
    #    main.TaskEdit.as_view(), name='task-edit'),
    url(r"^(?P<pslug>[\w\d\-]+)/backlog/", include(backlog_patterns)),
    url(r"^(?P<pslug>[\w\d\-]+)/dashboard/", include(dashboard_patterns)),
    url(r"^(?P<pslug>[\w\d\-]+)/milestone/", include(milestone_patterns)),
    url(r"^(?P<pslug>[\w\d\-]+)/issues/", include(issues_patterns)),
    url(r"^(?P<pslug>[\w\d\-]+)/tasks/", include(tasks_patterns)),
    url(r"^(?P<pslug>[\w\d\-]+)/uss/", include(userstories_patterns)),
)
