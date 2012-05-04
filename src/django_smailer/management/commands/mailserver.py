# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.core.mail import get_connection
from django.conf import settings
from optparse import make_option
from Queue import Queue

import importlib
import threading

import logging

log = logging.getLogger('greenmine.mail')

from django_smailer.settings import SMAILER_EMAIL_BACKEND, SMAILER_BIND_ADDRESS


class MailDispatcher(threading.Thread):
    def __init__(self, queue):
        super(MailDispatcher, self).__init__()
        self.queue = queue

    def run(self):
        while True:
            connection = get_connection(backends=SMAILER_EMAIL_BACKEND)
            messages = self.queue.get(True)
            connection.send_messages(messages)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--socket', action="store", dest="socket", default=SMAILER_BIND_ADDRESS,
            help="Tells tornado server to use this zmq push socket path instead a default."),
    )

    help = "Starts a internal maildispatcher."
    args = "[]"

    def handle(self, *args, **options):
        ctx = zmq.Context.instance()
        socket = ctx.socket(zmq.REP)
        socket.bind(options.socket)

        work_queue = Queue()
        dispatcher = MailDispatcher(queue)
        dispatcher.start()

        while True:
            _obj = socket.recv_pyobj()
            work_queue.put(_obj)
            socket.send_pyobj(len(_obj))
