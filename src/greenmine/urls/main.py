# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from greenmine.views import main, config, export
from django.conf import settings


js_info_dict = {
    'packages': ('greenmine',),
}

urlpatterns = patterns('',
    url(r'^$', main.HomeView.as_view(), name='projects'),
    url(r'^login/$', main.LoginView.as_view(), name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='auth_logout'),
    url(r'^remember-password/$', main.RememberPasswordView.as_view(), name='remember-password'),

    url(r'^register/$', main.RegisterView.as_view(), name='register'),

    url(r'^profile/$', 
        main.ProfileView.as_view(), name='profile'),

    url(r'^profile/password/change/$',
        main.PasswordChangeView.as_view(), name='profile-password'),

    url(r'^users/$', main.UserList.as_view(), name='users'),
    url(r'^users/create/$', main.UserCreateView.as_view(), name='users-create'),
    url(r'^users/(?P<uid>\d+)/view/$', main.UserView.as_view(), name='users-view'),
    url(r'^users/(?P<uid>\d+)/edit/$', main.UserEditView.as_view(), name='users-edit'),
    url(r'^users/(?P<uid>\d+)/delete/$', main.UserDelete.as_view(), name='users-delete'),
    url(r'^users/(?P<uid>\d+)/send/recovery/password/',
        main.SendRecoveryPasswordView.as_view(), name='users-recovery-password'),

    url(r'^project/create/$', 
        main.ProjectCreateView.as_view(), name='project-create'),

    url(r'^(?P<pslug>[\w\d\-]+)/settings/personal/$', 
        main.ProjectSettings.as_view(), name='project-personal-settings'),

    url(r'^(?P<pslug>[\w\d\-]+)/settings/general/$',
        main.ProjectGeneralSettings.as_view(), name='project-general-settings'),

    url(r'^(?P<pslug>[\w\d\-]+)/settings/edit/$',
        main.ProjectEditView.as_view(), name="project-edit"),
    
    url(r'^(?P<pslug>[\w\d\-]+)/settings/export/$', 
        export.ProjectExportView.as_view(), name="project-export-settings"),

    url(r'^(?P<pslug>[\w\d\-]+)/settings/export/now/$', 
        export.ProjectExportNow.as_view(), name="project-export-settings-now"),

    url(r'^(?P<pslug>[\w\d\-]+)/settings/export/rehash/',
        export.RehashExportsDirectory.as_view(), name="project-export-settings-rehash"),
    
    url(r'^(?P<pslug>[\w\d\-]+)/backlog/$', 
        main.BacklogView.as_view(), name='project-backlog'),

    url(r'^(?P<pslug>[\w\d\-]+)/dashboard/$', 
        main.DashboardView.as_view(), name="dashboard"),

    url(r'^(?P<pslug>[\w\d\-]+)/dashboard/(?P<mid>(?:\d+|unassigned))/$',
        main.DashboardView.as_view(), name="dashboard"),

    url(r'^(?P<pslug>[\w\d\-]+)/milestone/create/$', 
        main.MilestoneCreateView.as_view(), name='milestone-create'),

    url(r'^(?P<pslug>[\w\d\-]+)/questions/$', 
        main.QuestionsListView.as_view(), name='questions'),
    
    url(r'^(?P<pslug>[\w\d\-]+)/questions/create/$', 
        main.QuestionsCreateView.as_view(), name='questions-create'),

    url(r'^(?P<pslug>[\w\d\-]+)/questions/(?P<qslug>[\w\d\-]+)/view/$', 
        main.QuestionsView.as_view(), name='questions-view'),

    url(r'^(?P<pslug>[\w\d\-]+)/questions/(?P<qslug>[\w\d\-]+)/edit/$', 
        main.QuestionsEditView.as_view(), name='questions-edit'),

    url(r'^(?P<pslug>[\w\d\-]+)/questions/(?P<qslug>[\w\d\-]+)/delete/$',
        main.QuestionsDeleteView.as_view(), name='questions-delete'),

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
    
    # Task
    url(r'^(?P<pslug>[\w\d\-]+)/task/create/$',
        main.TaskCreateView.as_view(), name='task-create'),

    url(r'^(?P<pslug>[\w\d\-]+)/task/(?P<tref>[\w\d]+)/edit/$',
        main.TaskEdit.as_view(), name='task-edit'),

    url(r'^(?P<pslug>[\w\d\-]+)/task/(?P<tref>[\w\d]+)/view/$',
        main.TaskView.as_view(), name='task-view'),

    url(r'^(?P<pslug>[\w\d\-]+)/task/(?P<tref>[\w\d]+)/delete/$',
        main.TaskDelete.as_view(), name='task-delete'),
    
    # tasks/bugs view
    url(r'^(?P<pslug>[\w\d\-]+)/task/list/$',
        main.TasksView.as_view(), name='tasks-view'),
    
    url(r'^(?P<pslug>[\w\d\-]+)/milestone/(?P<mid>\d+)/task/list/$',
        main.TasksView.as_view(), name='tasks-view'),
    

    url(r'^password/recovery/(?P<token>[\d\w\-]+)/$', 
        main.PasswordRecoveryView.as_view(), name='password-recovery'),
        
    url(r'^(?P<pslug>[\w\d\-]+)/user-story/(?P<iref>[\d\w]+)/unassign/$',   
        main.UnassignUserStory.as_view(), name="unassign-us"),

    url(r'^(?P<pslug>[\w\d\-]+)/user-story/(?P<iref>[\d\w]+)/assign/$',
        main.AssignUserStory.as_view(), name="assign-us"),

    url(r'^(?P<pslug>[\w\d\-]+)/wiki/(?P<wslug>[\d\w\-]+)/$',
        main.WikiPageView.as_view(), name='wiki-page'),

    url(r'^(?P<pslug>[\w\d\-]+)/wiki/edit/(?P<wslug>[\d\w\-]+)/$',
        main.WikiPageEditView.as_view(), name='wiki-page-edit'),
)

urlpatterns += patterns('',
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict, name='jsi18n'),
)
