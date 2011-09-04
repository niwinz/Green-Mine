``django-randomfilenamestorage``
================================

A Django storage backend that gives random names to files.

By default, ``django.core.files.storage.FileSystemStorage`` deals with
conflicting filenames by appending an underscore to the file. For
instance, if you try to create ``hello.txt`` when it already exists,
it will rename it as ``hello_.txt``.

``django-randomfilenamestorage`` creates random filenames, so if you
try to create ``hello.txt``, it will save it as
``7z0a8m25sh9fyitx.txt``. Directory names and extensions are
preserved, only the root filename is randomized.

Installing
----------

The easiest way to install ``django-randomfilenamestorage`` is to use
**pip**::

    pip install django-randomfilenamestorage


Quick Start
-----------

In your Django ``settings`` file:

* Set ``DEFAULT_FILE_STORAGE`` to
  ``'django_randomfilenamestorage.storage.RandomFilenameFileSystemStorage'``

* Optionally, add ``'django-dbstorage'`` to ``INSTALLED_APPS``

This gives you random filenames, backed on Django's
``FileSystemStorage`` storage class.


``RandomFilenameMetaStorage``
-----------------------------

You can define a new underlying storage class by using
``RandomFilenameMetaStorage`` to wrap it::

    from django.core.files.storage import get_storage_class

    from django_randomfilenamestorage.storage import RandomFilenameMetaStorage

    RandomFilenameMyStorage = RandomFilenameMetaStorage(
        storage_class=get_storage_class('myapp.storage.MyStorage'),
    )

RandomFilenameMetaStorage defaults to 16-character root filenames.  To
change the default, define
``settings.RANDOM_FILENAME_LENGTH`` to a different integer
value.

To change the filename length of a wrapped storage class, pass in a
``length`` argument to ``RandomFilenameMetaStorage``. To override it
for a particular storage instance, pass in a ``randomfilename_length``
argument to its constructor.


Efficient random filename generation
------------------------------------

RandomFilenameMetaStorage is careful about not overwriting existing
files, on creation. Unfortunately, many storage classes do not throw
an ``OSError`` with ``EEXISTS`` when they detect a duplicate file on
``_save()``. 

If the underlying storage class accepts ``uniquify_names=False`` in
its constructor, ``RandomFilenameMetaStorage`` will reduce the number
of round-trips to the underlying storage class and make random
filename generation more efficient.

Safe storage classes include:

* ``django_randomfilenamestorage.storage.SafeFileSystemStorage``
* `django-dbstorage`_.


.. Links

.. _django-dbstorage:
   http://pypi.python.org/pypi/django-dbstorage
