# -*- coding: utf-8 -*- 
from django.conf.urls.defaults import patterns, include, url

from greenmine.views import api

urlpatterns = patterns('',
    url(r'^autocomplete/user/list/$', api.UserListApiView.as_view(), name='user-list'),

    url(r'^project/(?P<pslug>[\w\d\-]+)/task/(?P<taskref>[\w\d]+)/alter/$',
        api.TaskAlterApiView.as_view(), name="task-alter"),

    url(r'^i18n/lang/$', api.I18NLangChangeApiView.as_view(), 
        name='i18n-setlang'),

    url(r'^project/(?P<pslug>[\w\d\-]+)/task/(?P<taskref>[\w\d]+)/reassingn/$',
        api.TaskReasignationsApiView.as_view(), name='task-reassing'),
)

