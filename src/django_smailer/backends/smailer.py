# -*- coding: utf-8 -*-

from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings

import zmq

from django_smailer.settings import SMAILER_BIND_ADDRESS


class SmailerBackend(BaseEmailBackend):
    def create_socket(self):
        ctx = zmq.Context.instance()
        socket = ctx.socket(zmq.REQ)
        socket.connect(SMAILER_BIND_ADDRESS)

    def send_messages(self, messages):
        sock = self.create_socket()
        sock.send_pyobj(messages)

        poll_res = sock.poll(1)
        print poll_res

        if poll_res == 0:
            print "Message not sended"
            return 0

        ok = sock.recv_pyobj()
        if ok != len(messages):
            print "Message not sended (server error)"
            return 0

        return len(messages)
