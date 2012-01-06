# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from greenmine.views import main, config
from django.conf import settings


js_info_dict = {
    'packages': ('greenmine',),
}

urlpatterns = patterns('',
    url(r'^$', main.HomeView.as_view(), name='projects'),
    url(r'^login/$', main.LoginView.as_view(), name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='auth_logout'),

    url(r'^config/profile/$', 
        config.ProfileView.as_view(), name='profile'),

    url(r'^config/projects/$', 
        config.AdminProjectsView.as_view(), name='admin-projects'),

    url(r'^config/projects/(?P<pslug>[\w\d\-]+)/export/$',
            config.AdminProjectExport.as_view(), name="admin-project-export"),

    url(r'^project/create/$', 
        main.ProjectCreateView.as_view(), name='project-create'),
    
    url(r'^(?P<pslug>[\w\d\-]+)/backlog/$', 
        main.BacklogView.as_view(), name='project-backlog'),

    url(r'^(?P<pslug>[\w\d\-]+)/dashboard/$', 
        main.DashboardView.as_view(), name="dashboard"),

    url(r'^(?P<pslug>[\w\d\-]+)/dashboard/(?P<mid>(?:\d+|unassigned))/$',
        main.DashboardView.as_view(), name="dashboard"),

    url(r'^(?P<pslug>[\w\d\-]+)/user-story/create/$', 
        main.UserStoryCreateView.as_view(), name='user-story-create'),

    url(r'^(?P<pslug>[\w\d\-]+)/(?P<mid>\d+)/user-story/create/',
        main.UserStoryCreateView.as_view(), name='user-story-create'),

    url(r'^(?P<pslug>[\w\d\-]+)/user-story/(?P<iref>[\d\w]+)/edit/$',
        main.UserStoryEditView.as_view(), name='user-story-edit'),

    url(r'^(?P<pslug>[\w\d\-]+)/user-story/(?P<iref>[\d\w]+)/delete/$',
        main.UserStoryDeleteView.as_view(), name='user-story-delete'),

    url(r'^(?P<pslug>[\w\d\-]+)/user-story/(?P<iref>[\d\w]+)/task/create/$',
        main.TaskCreateView.as_view(), name='task-create'),

    url(r'^(?P<pslug>[\w\d\-]+)/user-story/(?P<iref>[\d\w]+)/task/(?P<tref>[\w\d]+)/edit/$',
        main.TaskEditView.as_view(), name='task-edit'),

    url(r'^(?P<pslug>[\w\d\-]+)/user-story/(?P<iref>[\w\d]+)/$', 
        main.UserStoryView.as_view(), name='user-story'),

    url(r'^password/recovery/(?P<token>[\d\w\-]+)/$', 
        main.PasswordRecoveryView.as_view(), name='password-recovery'),
        
    url(r'^(?P<pslug>[\w\d\-]+)/edit/$',
        main.ProjectEditView.as_view(), name="project-edit")        
)

urlpatterns += patterns('',
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict, name='jsi18n'),
)
