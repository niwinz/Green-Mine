"""
URL patterns to serve files from ``django_dbstorage``.

You can either use it as a module::

    url(r'^media/', include('django_dbstorage.urls'))

Or you can customize how the files are served::

    url(r'^media/',
        include(django_dbstorage.urls.serve(document_root='/root',
                                            show_indexes=True,
                                            name='serve')))
"""
from django.conf.urls.defaults import patterns, url


def serve(document_root=None, show_indexes=False,
          storage_class='django_dbstorage.storage.DatabaseStorage',
          name='dbstorage_serve'):
    """
    Returns URL patterns for the DatabaseStorage with several options.

    *document_root*
        See ``django_dbstorage.views.serve``.

    *show_indexes*
        See ``django_dbstorage.views.serve``.

    *storage_class*
        Specify a different DatabaseStorage class to use for serving
        files. This is useful if it has been subclassed.

    *name*
        Name the URL. Useful if serving from multiple URLs.
    """
    return patterns(
        '',
        url(r'^(?P<path>.*)$', 'django_dbstorage.views.serve',
            name=name,
            kwargs={'document_root': document_root,
                    'show_indexes': show_indexes,
                    'storage_class': storage_class}),
    )


#: Default ``urlpatterns`` so you can ``include('django_dbstorage.urls')``
urlpatterns = serve()
