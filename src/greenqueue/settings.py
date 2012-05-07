# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

GREENQUEUE_BIND_ADDRESS = getattr(settings, 'GREENQUEUE_BIND_ADDRESS', 'ipc:///tmp/greenqueue.sock')
GREENQUEUE_TASK_MODULES = getattr(settings, 'GREENQUEUE_TASK_MODULES', [])
GREENQUEUE_BACKEND = getattr(settings, 'GREENQUEUE_BACKEND', 'greenqueue.backends.zeromq.ZMQService')
