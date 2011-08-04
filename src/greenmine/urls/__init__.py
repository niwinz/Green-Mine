# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from greenmine.views import HomeView, LoginView 

urlpatterns = patterns('',
    #url(r'^api/', include('greenmine.urls.api')),
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^login/$', LoginView.as_view(), name='login'),
)


# Djangojs domain tranlation strings (gettext for js)
urlpatterns += patterns('',
    (r'^jsi18n/(?P<packages>\S+?)/$', 'django.views.i18n.javascript_catalog'),
)

# Static files managed with django.
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()
