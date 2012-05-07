# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from optparse import make_option

import logging
import zmq
import sys
import os

log = logging.getLogger('greenqueue')

from greenqueue.settings import GREENQUEUE_BIND_ADDRESS, GREENQUEUE_TASK_MODULES


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--socket', action="store", dest="socket", default=GREENQUEUE_BIND_ADDRESS,
            help="Tells greenqueue server to use this zmq push socket path instead a default."),
    )

    help = "Starts a greenqueue worker."
    args = "[]"

    def handle(self, *args, **options):
        ctx = zmq.Context.instance()

        socket = ctx.socket(zmq.SUB)
        socket.setsockopt(zmq.SUBSCRIBE, "")
        socket.bind(options['socket'])
        
        log.info("greenqueue: now listening on %s. (pid %s)", options['socket'], os.getpid())

        #try:
        #    while True:
        #        messages = socket.recv_pyobj()
        #        log.debug("smailer-server: now sending %s mails.", len(messages))
        #        connection = get_connection(backend=SMAILER_EMAIL_BACKEND)
        #        connection.send_messages(messages)

        #except KeyboardInterrupt:
        #    log.debug("smailer-server: stoping workers.")
        #    socket.close()
        #    sys.exit(0)
