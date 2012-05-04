# -*- coding: utf-8 -*-

from multiprocessing import Process, Queue


gqueue = Queue()
gprocess = None

def mailer_process_callback(queue):
    while True:
        email_object = queue.get()
        email_object.send()


def send_mail(email_object):
    global gqueue, gprocess

    gqueue.put(email_object)
    
    if gprocess is None:
        gprocess = Process(target=mailer_process_callback, args=(gqueue,))
        gprocess.start()
