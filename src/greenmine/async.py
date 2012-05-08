# -*- coding: utf-8 -*-

import logging
log = logging.getLogger('greenqueue')

from greenqueue.core import Library

register = Library()


@register.task(name='hello.world')
def hello_world(name):
    log.debug("DEBUG: Hello %s", name)
