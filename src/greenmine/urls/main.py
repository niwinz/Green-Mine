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
    url(r'^config/profile/$', config.ProfileView.as_view(), name='profile'),
    url(r'^config/projects/$', config.AdminProjectsView.as_view(), name='admin-projects'),
    url(r'^config/projects/(?P<pslug>[\w\d\-]+)/export/$',
        config.AdminProjectExport.as_view(), name="admin-project-export"),
    url(r'^project/create/$', main.ProjectCreateView.as_view(), name='project-create'),
    url(r'^(?P<pslug>[\w\d\-]+)/dashboard/$', main.MainDashboardView.as_view(), name='project'),
    url(r'^(?P<pslug>[\w\d\-]+)/dashboard/mid/(?P<mid>\d+)/$',
        main.MilestoneDashboardView.as_view(), name="milestone-dashboard"),

    url(r'^(?P<pslug>[\w\d\-]+)/us/(?P<iref>[\w\d]+)/$', main.UsView.as_view(), name='us'),
)

urlpatterns += patterns('',
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict, name='jsi18n'),
)

