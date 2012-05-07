# -*- coding: utf-8 -*-

from django.core.exceptions import ImproperlyConfigured
from greenmine.utils import Singleton

class Library(object):
    __metaclass__ = Singleton

    def __init__(self):
        self._tasks = {}

    def task(self, name=None, compile_function=None):
        if name is None and compile_function is None:
            # @register.tag()
            return self.task_function
        elif name is not None and compile_function is None:
            if callable(name):
                # @register.tag
                return self.task_function(name)
            else:
                # @register.tag('somename') or @register.tag(name='somename')
                def dec(func):
                    return self.task(name, func)
                return dec
        elif name is not None and compile_function is not None:
            # register.tag('somename', somefunc)
            self._tasks[name] = compile_function
            return compile_function
        else:
            raise ImproperlyConfigured("invalid task registration")

    def task_function(self, func):
        self._tasks[getattr(func, "_decorated_function", func).__name__] = func
        return func
