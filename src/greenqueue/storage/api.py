# -*- coding: utf-8 -*-

from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

def get_storage_backend(path=None, **kwargs):
    """
    Load storage backend.
    """

    path = path or getattr(settings, "GREENQUEUE_RESULTS_BACKEND",
        "greenqueue.storage.backends.model.StorageBackend")

    try:
        mod_name, klass_name = path.rsplit('.', 1)
        mod = import_module(mod_name)
    except AttributeError as e:
        raise ImproperlyConfigured(u'Error importing storage backend %s: "%s"' % (mod_name, e))

    try:
        klass = getattr(mod, klass_name)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" class' % (mod_name, klass_name))

    return klass(**kwargs)
