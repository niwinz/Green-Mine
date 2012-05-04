# -*- coding: utf-8 -*-


SMAILER_EMAIL_BACKEND = getattr(settings, 'SMAILER_EMAIL_BACKEND', 
    'django.core.mail.backends.locmem.EmailBackend')

SMAILER_BIND_ADDRESS = getattr(settings, 'SMAILER_BIND_ADDRESS', 'ipc:///tmp/smailer.sock')
