# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings


js_info_dict = {
    'packages': ('greenmine',),
}

from greenmine.base.views import api
from greenmine.base.views import config

from greenmine.scrum.views import main


internapi_urlpatterns = patterns('',
    url(r'^autocomplete/user/list/$', api.UserListApiView.as_view(), name='user-list'),
    url(r'^i18n/lang/$', api.I18NLangChangeApiView.as_view(),
        name='i18n-setlang'),
)

# FIXME: project administration is pending to refactor.
main_patterns = patterns('',
    url(r'^$', main.HomeView.as_view(), name='projects'),
    url(r'^users/$', main.UserList.as_view(), name='users'),
    url(r'^users/create/$', main.UserCreateView.as_view(), name='users-create'),
    url(r'^users/(?P<uid>\d+)/view/$', main.UserView.as_view(), name='users-view'),
    url(r'^users/(?P<uid>\d+)/edit/$', main.UserEditView.as_view(), name='users-edit'),
    url(r'^users/(?P<uid>\d+)/delete/$', main.UserDelete.as_view(), name='users-delete'),
    url(r'^users/(?P<uid>\d+)/send/recovery/password/',
        main.SendRecoveryPasswordView.as_view(), name='users-recovery-password'),
)

urlpatterns = patterns('',
    url(r"^auth/", include("greenmine.profile.urls")),
    url(r"^project/", include("greenmine.scrum.urls")),
    url(r"^project/(?P<pslug>[\w\d\-]+)/wiki/", include("greenmine.wiki.urls")),
    url(r"^project/(?P<pslug>[\w\d\-]+)/questions/", include("greenmine.questions.urls")),
    url(r"^project/(?P<pslug>[\w\d\-]+)/documents/", include("greenmine.documents.urls")),
    url(r'^search/', include('greenmine.search.urls')),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict, name='jsi18n'),
    url(r"^intern-api/", include(internapi_urlpatterns, namespace='api')),

    url(r"^", include(main_patterns)),
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
