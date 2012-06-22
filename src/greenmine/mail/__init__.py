# -*- coding: utf-8 -*-

from Queue import Queue
from django.core.mail import EmailMessage
from greenmine.utils import Singleton

import thread
import logging

log = logging.getLogger('asyncmail')

class AsyncMailSender(object):
    __metaclass__ = Singleton
    __queue__ = Queue(1000)

    def __init__(self):
        def mailer_worker(this):
            counter = 0
            while True:
                mail = this.__queue__.get(True)
                mail.send()

                log.info('Email message sended (%s)', counter)
                counter += 1

        log.info('Initializing asyncronous mail service.')
        thread.start_new_thread(mailer_worker, (self,))

    def __call__(self, *args, **kwargs):
        if len(args) > 0:
            for mailobj in args:
                if isinstance(mailobj, EmailMessage):
                    self.__queue__.put(mailobj, False)
        else:
            mailobj = EmailMessage(**kwargs)
            self.__queue__.put(mailobj, False)

    def queue_size(self):
        return self.__queue__.qsize()

send_mail = AsyncMailSender()
