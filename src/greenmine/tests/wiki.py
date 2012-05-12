# -*- coding: utf-8 -*-

from django.test import TestCase
from django.core import mail
from django.core.urlresolvers import reverse
import json

from django.contrib.auth.models import User
from ..models import *


class WikiRelatedTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(
            username = 'test',
            email = 'test@test.com',
            is_active = True,
            is_staff = False,
            is_superuser = False,
        )
        self.user1.set_password('test')
        self.user1.save()

        self.user2 = User.objects.create(
            username = 'test2',
            email = 'test2@test.com',
            is_active = True,
            is_staff = True,
            is_superuser = True,
            password = self.user1.password,
        )

        Project.objects.bulk_create([
            Project(name='test1', description='test1', owner=self.user1, slug='test1'),
            Project(name='test2', description='test2', owner=self.user1, slug='test2'),
            Project(name='test3', description='test3', owner=self.user2, slug='test3'),
        ])

        self.client.login(username='test', password='test')

    def tearDown(self):
        WikiPageHistory.objects.all().delete()
        WikiPage.objects.all().delete()
        Project.objects.all().delete()
        User.objects.all().delete()
        self.client.logout()
        mail.outbox = []

    def test_create_wikipage(self):
        project = Project.objects.get(name='test1')
        project.add_user(self.user1, "developer")

        url = reverse('web:wiki-page-edit', args=[project.slug, 'test'])

        params = {
            'content': 'test content',
        }

        response = self.client.post(url, params, follow=True)
        self.assertEqual(response.redirect_chain, [('http://testserver/test1/wiki/test/', 302)])
        self.assertEqual(response.status_code, 200)

        self.assertEqual(project.wiki_pages.count(), 1)

    def test_wikipage_history(self):
        project = Project.objects.get(name='test1')
        project.add_user(self.user1, "developer")

        wp = WikiPage.objects.create(
            project = project,
            content = 'test',
            slug = 'test',
            owner = self.user1,
        )

        url = reverse('web:wiki-page-edit', args=[project.slug, wp.slug])
        params = {
            'content': 'test2',
        }

        response = self.client.post(url, params, follow=True)
        self.assertEqual(response.redirect_chain, [('http://testserver/test1/wiki/test/', 302)])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(project.wiki_pages.count(), 1)
        self.assertEqual(wp.history_entries.count(), 1)
