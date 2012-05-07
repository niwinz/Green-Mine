# -*- coding: utf-8 -*-

from greenmine.utils import Singleton

class BaseStorageBackend(object):
    __metaclass__ = Singleton

    def save(self, uuid, result):
        raise NotImplementedError
