# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings


js_info_dict = {
    'packages': ('greenmine',),
}

#from greenmine.views import api
from greenmine.base.views import main
from greenmine.base.views import config
from greenmine.base.views import export
from greenmine.scrum.views import dashboard
from greenmine.scrum.views import backlog
from greenmine.scrum.views import issues
from greenmine.scrum.views import tasks


api_urlpatterns = patterns('',
    url(r'^autocomplete/user/list/$', api.UserListApiView.as_view(), name='user-list'),
    url(r'^i18n/lang/$', api.I18NLangChangeApiView.as_view(),
        name='i18n-setlang'),
)

main_patterns = patterns('',
    url(r'^$', main.HomeView.as_view(), name='projects'),
    url(r'^login/$', main.LoginView.as_view(), name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='auth_logout'),
    url(r'^remember-password/$', main.RememberPasswordView.as_view(), name='remember-password'),

    url(r'^register/$', main.RegisterView.as_view(), name='register'),
    url(r'^activate/(?P<token>[\d\w\-]+)/$',
        main.AccountActivation.as_view(), name='activate'),

    url(r'^profile/$',
        main.ProfileView.as_view(), name='profile'),

    url(r'^profile/password/change/$',
        main.PasswordChangeView.as_view(), name='profile-password'),

    url(r'^password/recovery/(?P<token>[\d\w\-]+)/$',
        main.PasswordRecoveryView.as_view(), name='password-recovery'),

    url(r'^users/$', main.UserList.as_view(), name='users'),
    url(r'^users/create/$', main.UserCreateView.as_view(), name='users-create'),
    url(r'^users/(?P<uid>\d+)/view/$', main.UserView.as_view(), name='users-view'),
    url(r'^users/(?P<uid>\d+)/edit/$', main.UserEditView.as_view(), name='users-edit'),
    url(r'^users/(?P<uid>\d+)/delete/$', main.UserDelete.as_view(), name='users-delete'),
    url(r'^users/(?P<uid>\d+)/send/recovery/password/',
        main.SendRecoveryPasswordView.as_view(), name='users-recovery-password'),

    url(r'^project/create/$',
        main.ProjectCreateView.as_view(), name='project-create'),

    url(r'^(?P<pslug>[\w\d\-]+)/delete/$',
        main.ProjectDelete.as_view(), name='project-delete'),

    # User storys
    url(r'^(?P<pslug>[\w\d\-]+)/user-story/create/$',
        main.UserStoryCreateView.as_view(), name='user-story-create'),

    url(r'^(?P<pslug>[\w\d\-]+)/(?P<mid>\d+)/user-story/create/',
        main.UserStoryCreateView.as_view(), name='user-story-create'),

    url(r'^(?P<pslug>[\w\d\-]+)/user-story/(?P<iref>[\d\w]+)/edit/$',
        main.UserStoryEdit.as_view(), name='user-story-edit'),

    url(r'^(?P<pslug>[\w\d\-]+)/user-story/(?P<iref>[\d\w]+)/edit-inline/$',
        main.UsFormInline.as_view(), name='user-story-edit-inline'),

    url(r'^(?P<pslug>[\w\d\-]+)/user-story/(?P<iref>[\d\w]+)/delete/$',
        main.UserStoryDeleteView.as_view(), name='user-story-delete'),

    url(r'^(?P<pslug>[\w\d\-]+)/user-story/(?P<iref>[\w\d]+)/$',
        main.UserStoryView.as_view(), name='user-story'),

    # API
    url(r'^(?P<pslug>[\w\d\-]+)/user-story/(?P<iref>[\d\w]+)/unassign/$',
        main.UnassignUserStory.as_view(), name="unassign-us"),

    url(r'^(?P<pslug>[\w\d\-]+)/user-story/(?P<iref>[\d\w]+)/assign/$',
        main.AssignUserStory.as_view(), name="assign-us"),

    #url(r'^(?P<pslug>[\w\d\-]+)/task/(?P<tref>[\w\d]+)/edit/$',
    #    main.TaskEdit.as_view(), name='task-edit'),
)

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

project_settings_patterns = patterns('',
    url(r'^personal/$', main.ProjectSettings.as_view(), name='project-personal-settings'),
    url(r'^general/$', main.ProjectGeneralSettings.as_view(), name='project-general-settings'),
    url(r'^edit/$', main.ProjectEditView.as_view(), name="project-edit"),

    # export (not finished)
    url(r'^export/$', export.ProjectExportView.as_view(), name="project-export-settings"),
    url(r'^export/now/$', export.ProjectExportNow.as_view(), name="project-export-settings-now"),
    url(r'^export/rehash/', export.RehashExportsDirectory.as_view(), name="project-export-settings-rehash"),
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
)

milestone_patterns = patterns('',
    url(r'^create/$', main.MilestoneCreateView.as_view(), name='milestone-create'),
    url(r'^(?P<mid>\d+)/edit/$', main.MilestoneEditView.as_view(), name='milestone-edit'),
    url(r'^(?P<mid>\d+)/delete/$', main.MilestoneDeleteView.as_view(), name='milestone-delete'),
)

documents_patterns = patterns('',
    url(r'^$', main.Documents.as_view(), name='documents'),
    url(r'^(?P<docid>\d+)/delete/$', main.DocumentsDelete.as_view(), name='documents-delete'),
)

questions_patterns = patterns('',
    url(r'^$', main.QuestionsListView.as_view(), name='questions'),
    url(r'^create/$', main.QuestionsCreateView.as_view(), name='questions-create'),
    url(r'^(?P<qslug>[\w\d\-]+)/view/$', main.QuestionsView.as_view(), name='questions-view'),
    url(r'^(?P<qslug>[\w\d\-]+)/edit/$', main.QuestionsEditView.as_view(), name='questions-edit'),
    url(r'^(?P<qslug>[\w\d\-]+)/delete/$', main.QuestionsDeleteView.as_view(), name='questions-delete'),
)


wiki_patterns = patterns('',
    url(r'^(?P<wslug>[\d\w\-]+)/$', main.WikiPageView.as_view(), name='wiki-page'),
    url(r'^(?P<wslug>[\d\w\-]+)/history/$', main.WikiPageHistory.as_view(), name='wiki-page-history'),

    url(r'^(?P<wslug>[\d\w\-]+)/history/(?P<hpk>\d+)/$',
        main.WikiPageHistoryView.as_view(), name='wiki-page-history-view'),

    url(r'^(?P<wslug>[\d\w\-]+)/edit/$', main.WikiPageEditView.as_view(), name='wiki-page-edit'),
    url(r'^(?P<wslug>[\d\w\-]+)/delete/$', main.WikipageDeleteView.as_view(), name='wiki-page-delete'),
)

urlpatterns = patterns('',
    url(r"^(?P<pslug>[\w\d\-]+)/backlog/", include(backlog_patterns)),
    url(r"^(?P<pslug>[\w\d\-]+)/dashboard/", include(dashboard_patterns)),
    url(r"^(?P<pslug>[\w\d\-]+)/milestone/", include(milestone_patterns)),
    url(r"^(?P<pslug>[\w\d\-]+)/wiki/", include(wiki_patterns)),
    url(r"^(?P<pslug>[\w\d\-]+)/settings/", include(project_settings_patterns)),
    url(r"^(?P<pslug>[\w\d\-]+)/documents/", include(documents_patterns)),
    url(r"^(?P<pslug>[\w\d\-]+)/questions/", include(questions_patterns)),
    url(r"^(?P<pslug>[\w\d\-]+)/issues/", include(issues_patterns)),
    url(r"^(?P<pslug>[\w\d\-]+)/tasks/", include(tasks_patterns)),

    url(r"^", include(main_patterns)),
    url(r"^api/", include(api_urlpatterns, namespace='api')),

    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict, name='jsi18n'),
)


def mediafiles_urlpatterns():
    """
    Method for serve media files with runserver.
    """

    _media_url = settings.MEDIA_URL
    if _media_url.startswith('/'):
        _media_url = _media_url[1:]

    from django.views.static import serve
    return patterns('',
        (r'^%s(?P<path>.*)$' % _media_url, serve,
            {'document_root': settings.MEDIA_ROOT})
    )

urlpatterns += staticfiles_urlpatterns()
urlpatterns += mediafiles_urlpatterns()
