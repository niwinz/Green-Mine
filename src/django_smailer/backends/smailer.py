# -*- coding: utf-8 -*-

from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings

import zmq

from django_smailer.settings import SMAILER_BIND_ADDRESS

class SmailerBackend(BaseEmailBackend):
    def __init__(self, *args, **kwargs):
        super(SmailerBackend, self).__init__(*args, **kwargs)

    def create_socket(self):
        ctx = zmq.Context.instance()
        socket = ctx.socket(zmq.PUB)
        socket.connect(SMAILER_BIND_ADDRESS)
        return socket

    def send_messages(self, messages):
        sock = self.create_socket()
        sock.send_pyobj(messages)
        return len(messages)
