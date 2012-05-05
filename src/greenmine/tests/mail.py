# -*- coding: utf-8 -*-


from django.test import TestCase
from django.core import mail
from django.core.urlresolvers import reverse
from django.utils import simplejson as json

from django.contrib.auth.models import User
from ..models import *

from greenmine import permissions as perms
from django.utils import timezone
import datetime

from greenmine.utils import mail as mailutils


class LowLevelEmailTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username = 'test',
            email = 'test@test.com',
            is_active = True,
            is_staff = False,
            is_superuser = False,
        )
        self.user.set_password('test')
        self.user.save()
        mail.outbox = []

    def test_send_recovery_mail(self):
        mailutils.send_recovery_email(self.user)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Greenmine: password recovery.")

    def test_send_registration_mail(self):
        mailutils.send_new_registration_mail(self.user)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Greenmine: Welcome!")

