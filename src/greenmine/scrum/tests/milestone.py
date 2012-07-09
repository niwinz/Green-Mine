# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core import mail
from django.test import TestCase
from django.utils import timezone

from ..models import Project, Milestone
from ...core import permissions as perms

import datetime
import json

class MilestoneTests(TestCase):
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

        self.project1 = Project.objects\
            .create(name='test1', description='test1', owner=self.user1, slug='test1')

        self.project2 = Project.objects\
            .create(name='test2', description='test2', owner=self.user2, slug='test2')

        self.project1.add_user(self.user1, 'developer')
        self.project2.add_user(self.user2, 'developer')

    def tearDown(self):
        self.project1.delete()
        self.project2.delete()
        self.user2.delete()
        self.user1.delete()

    def test_view_create_page_milestone(self):
        response = self.client.get(self.project1.get_milestone_create_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['messages']), 0)

    def test_create_milestone(self):
        self.client.login(username="test1", password="test")

        post_params = {
            'name': 'test milestone',
            'estimated_finish': '02/02/2012',
            'estimated_start': '02/01/2012',
            'disponibility': 20,
        }

        response = self.client.post(self.project1.get_milestone_create_url(), post_params, follow=True)

        # expected redirect
        self.assertEqual(response.redirect_chain,  [('http://testserver/test1/backlog/', 302)])
        self.assertEqual(len(response.context['messages']), 0)

    def test_create_milestone_without_permissions(self):
        self.client.login(username="test2", password="test")

        post_params = {
            'name': 'test milestone',
            'estimated_finish': '02/02/2012',
            'estimated_start': '02/01/2012',
            'disponibility': 20,
        }


        response = self.client.post(self.project1.get_milestone_create_url(), post_params)
        self.assertEqual(response.status_code, 403)

    def test_create_milestone_without_permissions_superuser(self):
        self.client.login(username="test1", password="test")

        post_params = {
            'name': 'test milestone',
            'estimated_finish': '02/02/2012',
            'estimated_start': '02/01/2012',
            'disponibility': 20,
        }

        response = self.client.post(self.project2.get_milestone_create_url(), post_params, follow=True)
        self.assertEqual(response.redirect_chain,  [('http://testserver/test2/backlog/', 302)])
        self.assertEqual(len(response.context['messages']), 0)

    def test_delete_milestone(self):
        now_date = datetime.datetime.now(tz=timezone.get_default_timezone())

        milestone = Milestone.objects.create(
            project = self.project1,
            owner = self.user1,
            name = 'test milestone',
            estimated_finish = now_date + datetime.timedelta(20),
            estimated_start = now_date,
        )

        self.client.login(username='test1', password='test')
        response = self.client.post(milestone.get_delete_url(), {})
        self.assertEqual(response.status_code, 200)

        jdata = json.loads(response.content)
        self.assertIn("valid", jdata)
        self.assertTrue(jdata['valid'])

    def test_delete_milestone_without_permissions_superuser(self):
        now_date = datetime.datetime.now(tz=timezone.get_default_timezone())

        milestone = Milestone.objects.create(
            project = self.project2,
            owner = self.user2,
            name = 'test milestone',
            estimated_finish = now_date + datetime.timedelta(20),
            estimated_start = now_date,
        )

        self.client.login(username='test1', password='test')
        response = self.client.post(milestone.get_delete_url(), {})
        self.assertEqual(response.status_code, 200)

        jdata = json.loads(response.content)
        self.assertIn("valid", jdata)
        self.assertTrue(jdata['valid'])

    def test_delete_milestone_without_permissions(self):
        now_date = datetime.datetime.now(tz=timezone.get_default_timezone())

        milestone = Milestone.objects.create(
            project = self.project1,
            owner = self.user1,
            name = 'test milestone',
            estimated_finish = now_date + datetime.timedelta(20),
        )

        self.client.login(username='test2', password='test')
        response = self.client.post(milestone.get_delete_url(), {})
        self.assertEqual(response.status_code, 403)


