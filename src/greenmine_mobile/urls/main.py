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
    url(r'^profile/$', views.ProfileView.as_view(), name='profile'),
    url(r'^(?P<pslug>[\w\d\-]+)/dashboard/$', views.ProjectView.as_view(), name='project'),
    url(r'^(?P<pslug>[\w\d\-]+)/us/(?P<iref>[\w\d]+)/$', views.UsView.as_view(), name='us'),

    url(r'^(?P<pslug>[\w\d\-]+)/us/create/$', views.UsCreate.as_view(), name='us-create'),
    url(r'^(?P<pslug>[\w\d\-]+)/us/create/mid/(?P<mid>\d+)/$', views.UsCreate.as_view(), name='us-create'),

    # Api html calls
    url(r'^(?P<pslug>[\w\d\-]+)/milestone/(?P<mid>\d+)/uss/$',
        views.ProjectUssView.as_view(), name='project-uss-view'),
)

urlpatterns += patterns('',
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict, name='jsi18n'),
)
