``django-dbstorage``
====================

A Django file storage backend for files in the database.


Installing
----------

The easiest way to install ``django-dbstorage`` is to use **pip**::

    pip install django-dbstorage


Quick Start
-----------

In your Django ``settings`` file:

* Add ``'django-dbstorage'`` to ``INSTALLED_APPS``

* Set ``DEFAULT_FILE_STORAGE`` to
  ``'django_dbstorage.storage.DatabaseStorage'``

* Set ``MEDIA_ROOT`` and ``MEDIA_URL`` to ``None``.


Serving files
-------------

In your ``urls.py``, add the following to ``urlpatterns``::

   url(r'^media/', include('django_dbstorage.urls'))

Or, if you want to specify more options, use::

   url(r'^media/', include(django_dbstorage.urls.serve()))

You should set ``settings.MEDIA_URL`` to the root of this include, in
this case: ``/media/``.

If you do not wish to serve files from the database, don't add
anything to ``urls.py`` and set ``settings.MEDIA_URL`` to ``None``.


Customizing
-----------

``DatabaseStorage`` takes several options. To customize, subclass
it and use that as ``DEFAULT_FILE_STORAGE``. For instance::

    class MyDatabaseStorage(DatabaseStorage):
        def __init__(self):
            super(MyDatabaseStorage, self).__init__(location='/tmp',
                                                    base_url='/files/',
                                                    uniquify_names=True)

As a convenience, there is a ``NonUniquifyingDatabaseStorage`` class
which does not attempt to find a unique filename when saving. This
class throws an ``IOError`` with the ``EEXISTS`` status code, when
attempting to ``_save()``.

This functionality is used by other packages, such as
`django-randomfilenamestorage`_.


.. Links

.. _django-randomfilenamestorage:
   http://pypi.python.org/pypi/django-randomfilenamestorage
