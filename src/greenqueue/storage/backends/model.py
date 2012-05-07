# -*- coding: utf-8 -*-

from django.db import transaction
from greenqueue.models import TaskResult
from .base import BaseStorageBackend

try:
    import cPickle as pickle
except ImportError:
    import pickle

import base64

class StorageBackend(BaseStorageBackend):
    @transaction.commit_on_success
    def save(self, uuid, value):
        _val = pickle.dumps(value)
        tr = TaskResult.objects.create(uuid=uuid, \
            result=base64.b64encode(_val))
        return value
