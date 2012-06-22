# -*- coding: utf-8 -*-

from .development import *

import sys
sys.path.insert(0, '/home/niwi/devel/django-greenqueue')
sys.path.insert(0, '/home/niwi/devel/django-superview')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'greenmine',
        'USER': 'niwi',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}


#INSTALLED_APPS += ['redis_cache.stats']


import sys
sys.path.insert(0, '/home/niwi/devel/django-redis')

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.cache.RedisCache',
        'LOCATION': '127.0.0.1:6379',
        'OPTIONS': {
            'DB': 1,
            'PARSER_CLASS': 'redis.connection.HiredisParser'
        },
    },
}


GREENQUEUE_BACKEND = 'greenqueue.backends.zeromq.ZMQService'
#GREENQUEUE_WORKER_MANAGER = 'greenqueue.worker.pgevent.GreenletManager'

#GREENQUEUE_BACKEND = 'greenqueue.backends.rabbitmq.RabbitMQService'
GREENQUEUE_WORKER_MANAGER = 'greenqueue.worker.process.ProcessManager'

#GREENQUEUE_RABBITMQ_USERNAME = 'test'
#GREENQUEUE_RABBITMQ_PASSWORD = 'test'
#GREENQUEUE_RABBITMQ_VHOST = '/test'
