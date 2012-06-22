# -*- coding: utf-8 -*-

from django.test import TestCase
from django.core import mail
from django.core.urlresolvers import reverse

import json

from django.contrib.auth.models import User

class UserRelatedTests(TestCase):
    def create_sample_user(self):
        instance = User.objects.create(
            username = 'test',
            first_name = 'Foo',
            last_name = 'Bar',
            email = 'foo@bar.com',
            is_active = True,
            is_staff = False,
            is_superuser = False
        )

        instance.set_password("fooo")
        instance.save()
        return instance

    def tearDown(self):
        mail.outbox = []
        self.client.logout()
        User.objects.all().delete()

    def test_simple_register_and_activate(self):
        register_params = {
            'username': 'test',
            'first_name': 'Foo',
            'last_name': 'Bar',
            'email': 'foo@bar.com',
            'password': '123123',
            'password2': '123123',
        }

        register_url = reverse('web:register')
        response = self.client.post(register_url, register_params)
        self.assertEqual(response.status_code, 302)

        user = User.objects.get(username='test')

        self.assertTrue(user.get_profile())

        self.assertTrue(user.has_usable_password())
        self.assertFalse(user.is_active)

        # expected send 1 email
        self.assertEqual(len(mail.outbox), 1)

        activate_url = reverse('web:activate', args=[user.get_profile().token])
        response = self.client.get(activate_url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [('http://testserver/login/', 302)])

        user = User.objects.get(username='test')
        self.assertTrue(user.is_active)
        self.assertEqual(user.get_profile().token, None)

    def test_profile_view(self):
        user = self.create_sample_user()
        url = reverse("web:profile")

        ok = self.client.login(username='test', password='fooo')
        self.assertTrue(ok)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        instance = self.create_sample_user()

        post_params = {
            'username': instance.username,
            'password': 'fooo',
        }

        login_url = reverse('web:login')
        response = self.client.post(login_url, post_params,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)

        jdata = json.loads(response.content)
        self.assertTrue(jdata['valid'])

    def test_password_change(self):
        user = self.create_sample_user()
        change_password_url = reverse('web:profile-password')

        post_params = {
            'password': 'fofo',
            'password2': 'fofo',
        }

        response = self.client.post(change_password_url, post_params, follow=True)
        self.assertEqual(response.redirect_chain, [('http://testserver/login/', 302)])

        ok = self.client.login(username='test', password='fooo')
        self.assertTrue(ok)

        response = self.client.post(change_password_url, post_params, follow=True)
        self.assertEqual(response.redirect_chain, [('http://testserver/profile/', 302)])

    def test_profile_form(self):
        user = self.create_sample_user()

        post_params = {
            'first_name': 'Caco',
        }

        profile_url = reverse('web:profile')

        response = self.client.post(profile_url, post_params, follow=True)
        self.assertEqual(response.redirect_chain, [('http://testserver/login/', 302)])

        ok = self.client.login(username='test', password='fooo')
        self.assertTrue(ok)

        response = self.client.post(profile_url, post_params, follow=True)
        self.assertEqual(response.redirect_chain, [('http://testserver/profile/', 302)])

        user = User.objects.get(pk=user.id)
        self.assertEqual(user.first_name, 'Caco')
        self.assertEqual(user.last_name, '')
        self.assertEqual(user.username, 'test')
