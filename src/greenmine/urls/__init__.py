# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^api/', include('greenmine.urls.api', namespace='api')),
    url(r'^', include('greenmine.urls.main', namespace='web')),
)

# Djangojs domain tranlation strings (gettext for js)
urlpatterns += patterns('',
    (r'^jsi18n/(?P<packages>\S+?)/$', 'django.views.i18n.javascript_catalog'),
)

# Static files managed with django.
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()

from django.conf import settings

if settings.DEBUG:
    from django.views.static import serve
    _media_url = settings.MEDIA_URL
    if _media_url.startswith('/'):
        _media_url = _media_url[1:]
        urlpatterns += patterns('', 
            (r'^%s(?P<path>.*)$' % _media_url, serve, {'document_root': settings.MEDIA_ROOT})
        )
