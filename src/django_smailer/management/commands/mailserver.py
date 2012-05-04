# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.core.mail import get_connection
from django.conf import settings
from optparse import make_option
from Queue import Queue, Empty

import importlib
import threading

import logging
import zmq
import sys
import os

log = logging.getLogger('greenmine.mail.server')

from django_smailer.settings import SMAILER_EMAIL_BACKEND, SMAILER_BIND_ADDRESS


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--socket', action="store", dest="socket", default=SMAILER_BIND_ADDRESS,
            help="Tells tornado server to use this zmq push socket path instead a default."),
    )

    help = "Starts a internal maildispatcher."
    args = "[]"

    def handle(self, *args, **options):
        ctx = zmq.Context.instance()

        socket = ctx.socket(zmq.SUB)
        socket.setsockopt(zmq.SUBSCRIBE, "")
        socket.bind(options['socket'])
        
        log.info("smailer-server: now listening on %s. (pid %s)", options['socket'], os.getpid())

        try:
            while True:
                messages = socket.recv_pyobj()
                log.debug("smailer-server: now sending %s mails.", len(messages))
                connection = get_connection(backend=SMAILER_EMAIL_BACKEND)
                connection.send_messages(messages)

        except KeyboardInterrupt:
            log.debug("smailer-server: stoping workers.")
            socket.close()
            sys.exit(0)
