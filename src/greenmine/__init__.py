# -*- coding: utf-8 -*-

from django.db.backends.signals import connection_created
from django.dispatch import receiver

@receiver(connection_created)
def connection_created_handler(sender, connection, **kwargs):
    c = connection.cursor()
    c.execute('PRAGMA temp_store = MEMORY;')
    c.execute('PRAGMA synchronous = OFF;')
    c.execute('PRAGMA default_cache_size = 10000;')
    print "Connection created: ", connection


