# -*- coding: utf-8 -*-

from django.core.exceptions import ImproperlyConfigured
from .. import settings

#GREENQUEUE_BIND_ADDRESS = getattr(settings, 'GREENQUEUE_BIND_ADDRESS', 'ipc:///tmp/greenqueue.sock')
#GREENQUEUE_TASK_MODULES = getattr(settings, 'GREENQUEUE_TASK_MODULES', [])


class ZMQService(object):
    def __init__(self):

    def _validate(self):
        if not settings.GREENQUEUE_TASK_MODULES:
            raise ImproperlyConfigured("No tasks module especified")
        


