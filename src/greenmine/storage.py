# -*- coding: utf-8 -*-

from django.core.files.storage import get_storage_class
from django_randomfilenamestorage.storage import RandomFilenameMetaStorage

RandomFilenameDBStorage = RandomFilenameMetaStorage(
    storage_class=get_storage_class('django_dbstorage.storage.DatabaseStorage')
)


