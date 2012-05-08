# -*- coding: utf-8 -*-

from .storage.api import get_storage_backend

class AsyncResult(object)
    uuid = None
    error = False
    ready = False

    def __init__(self, uuid):
        self.uuid = uuid
        self.storage = get_storage_backend()

    def check(self, default=None):
        return self.storage.get(uuid, default)

        
