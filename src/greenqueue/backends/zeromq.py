# -*- coding: utf-8 -*-

from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from .. import settings
from ..core import Library
from ..storage import get_storage_backend

import logging, os
log = logging.getLogger('greenqueue')

class ZMQService(object):
    def __init__(self):
        self.lib = Library
        self.storage = get_storage_backend()

    @classmethod
    def setup_gevent_spawn(cls):
        # posible, but untested gevent enable for this backend
        # this is incomplete, need zmq gevent patching.
        # import gevent
        # cls._back_process_callable = cls.process_callable
        # def _wrapped_process_callable(self, uuid, _callable, args, kwargs)::
        #     gevent.spawn(self._back_process_callable, *args, **kwargs)
        # cls.process_callable = _wrapped_process_callable
        pass

    def load_modules(self):
        for modpath in settings.GREENQUEUE_TASK_MODULES:
            import_module(modpath)

    def zmq(self):
        return import_module('zmq')

    def start(self, socket_path=settings.GREENQUEUE_BIND_ADDRESS):
        # load all modules
        self.load_modules()
        
        # bind socket
        ctx = self.zmq().Context.instance()
        socket = ctx.socket(self.zmq().PULL)
        socket.bind(options['socket'])
        log.info("greenqueue: now listening on %s. (pid %s)", socket_path, os.getpid())

        # recv loop
        while True:
            message = socket.recv_pyobj()
            self.handle_message(message)

    def validate_message(self, message):
        name = None
        if "name" not in message:
            return False, name
        else:
            name = message['name']
        if "uuid" not in message:
            return False, name
        if "args" not in message:
            return False, name
        if "kwargs" not in message:
            return False, name
        return True, name

    def get_callable_for_task(self, task):
        # at the moment tasks only can be functions.
        # on future this can be implemented on Task class.
        return task

    def process_callable(self, uuid, _callable, args, kwargs):
        # at the moment process callables in serie.
        result = _callable(*args, **kwargs)

        # save result to result storag backend.
        self.storage.save(uuid, result)

    def handle_message(self, message):
        ok, name = self.validate_message(message)
        if not ok:
            log.error("greenqueue: ignoring invalid message")
            return
        
        try:
            _task = self.lib.task_by_name(name)
        except ValueError:
            log.error("greenqueue: received unknown or unregistret method call: %s", name)
            return
        
        task_callable = self.get_callable_for_task(_task)
        args, kwargs, uuid = message['args'], message['kwargs'], message['uuid']
        self.process_callable(uuid, task_callable, args, kwargs)
