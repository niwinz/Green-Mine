"""
Test URLs for django_dbstorage.tests.ViewsTestCase.
"""

from django.conf.urls.defaults import include, patterns, url

from django_dbstorage.urls import serve


urlpatterns = patterns(
    '',
    url(r'^urls/', include('django_dbstorage.urls')),
    url(r'^serve/', include(serve())),
    url(r'^indexes/', include(serve(show_indexes=True))),
    url(r'^root/', include(serve(document_root='root', show_indexes=True))),
)
