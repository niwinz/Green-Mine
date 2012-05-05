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


class UserMailTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(
            username = 'test1',
            email = 'test1@test.com',
            is_active = True,
            is_staff = True,
            is_superuser = True,
        )

        self.user2 = User.objects.create(
            username = 'test2',
            email = 'test2@test.com',
            is_active = True,
            is_staff = False,
            is_superuser = False,
        )

        self.user1.set_password("test")
        self.user2.set_password("test")

        self.user1.save()
        self.user2.save()

        mail.outbox = []

    def test_remember_password(self):
        url = reverse("web:remember-password")

        post_params = {'email': 'test2@test.com'}
        response = self.client.post(url, post_params, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)

        jdata = json.loads(response.content)
        self.assertIn("valid", jdata)
        self.assertTrue(jdata['valid'])

    def test_remember_password_not_exists(self):
        url = reverse("web:remember-password")

        post_params = {'email': 'test2@testa.com'}
        response = self.client.post(url, post_params, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

        jdata = json.loads(response.content)
        self.assertIn("valid", jdata)
        self.assertFalse(jdata['valid'])

    def test_send_recovery_password_by_staff(self):
        url = reverse("web:users-recovery-password", args=[self.user2.pk])
        
        ok = self.client.login(username="test1", password="test")
        self.assertTrue(ok)
        
        # pre test
        self.assertTrue(self.user2.is_active)
        self.assertEqual(self.user2.get_profile().token, None)

        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # expected redirect
        self.assertEqual(response.redirect_chain, [('http://testserver/users/2/edit/', 302)])

        # test mail sending
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Greenmine: password recovery.")

        # test user model modification
        self.user2 = User.objects.get(pk=self.user2.pk)
        self.assertTrue(self.user2.is_active)
        self.assertFalse(self.user2.has_usable_password())
        self.assertNotEqual(self.user2.get_profile().token, None)

        url = reverse('web:password-recovery', args=[self.user2.get_profile().token])

        post_params = {
            'password': '123123',
            'password2': '123123',
        }
        response = self.client.post(url, post_params, follow=True)

        self.assertEqual(response.status_code, 200)

        # expected redirect
        self.assertEqual(response.redirect_chain, [('http://testserver/login/', 302)])

        ok = self.client.login(username="test2", password="123123")
        self.assertTrue(ok)

