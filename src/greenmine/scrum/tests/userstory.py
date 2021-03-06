# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core import mail
from django.test import TestCase
from django.utils import timezone

from ..models import *
from ...core import permissions as perms

import datetime
import json


class UserStoriesTests(TestCase):
    def setUp(self):
        self.now_date = datetime.datetime.now(tz=timezone.get_default_timezone())

        self.user1 = User.objects.create(
            username = 'test1',
            email = 'test1@test.com',
            is_active = True,
            is_staff = True,
            is_superuser = True,
        )

        self.user1.set_password("test")
        self.user1.save()

        self.user2 = User.objects.create(
            username = 'test2',
            email = 'test2@test.com',
            is_active = True,
            is_staff = False,
            is_superuser = False,
            password = self.user1.password,
        )

        self.user3 = User.objects.create(
            username = 'test3',
            email = 'test3@test.com',
            is_active = True,
            is_staff = False,
            is_superuser = False,
            password = self.user1.password,
        )


        self.project1 = Project.objects\
            .create(name='test1', description='test1', owner=self.user1, slug='test1')

        self.project2 = Project.objects\
            .create(name='test2', description='test2', owner=self.user2, slug='test2')

        self.project1.add_user(self.user1, 'developer')
        self.project2.add_user(self.user2, 'developer')
        self.project2.add_user(self.user3, 'developer')

        self.milestone1 = Milestone.objects.create(
            project = self.project1,
            owner = self.user1,
            name = 'test1 milestone',
            estimated_finish = self.now_date + datetime.timedelta(20),
        )

        self.milestone2 = Milestone.objects.create(
            project = self.project2,
            owner = self.user2,
            name = 'test2 milestone',
            estimated_finish = self.now_date + datetime.timedelta(20),
        )
        mail.outbox = []

    def tearDown(self):
        self.milestone1.delete()
        self.milestone2.delete()
        self.project1.delete()
        self.project2.delete()
        self.user2.delete()
        self.user1.delete()

    def test_backlog_simple_view(self):
        self.client.login(username="test2", password="test")
        response = self.client.get(self.project2.get_backlog_url())
        self.assertEqual(response.status_code, 200)

    def test_backlog_simple_view_without_permissions(self):
        self.client.login(username="test2", password="test")
        response = self.client.get(self.project1.get_backlog_url())
        self.assertEqual(response.status_code, 403)

    def test_user_story_create_view_page(self):
        self.client.login(username="test2", password="test")
        response  = self.client.get(self.milestone2.get_user_story_create_url())
        self.assertEqual(response.status_code, 200)

    def test_user_story_create_view_page_without_permissions(self):
        self.client.login(username="test2", password="test")
        response  = self.client.get(self.milestone1.get_user_story_create_url())
        self.assertEqual(response.status_code, 403)

    def test_user_story_create_with_milestone(self):
        self.client.login(username="test2", password="test")

        post_params = {
            'priority': 3,
            'points': '10',
            'status': 'open',
            'category': '',
            'tested': False,
            'subject': 'test us',
            'description': 'test desc us',
            'finish_date': '02/02/2012',
        }

        response = self.client.post(self.milestone2.get_user_story_create_url(), post_params, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [('http://testserver/test2/backlog/', 302)])

        self.assertEqual(self.milestone2.user_stories.count(), 1)
        self.assertEqual(self.project2.user_stories.count(), 1)
        self.assertEqual(self.project2.tasks.count(), 0)
        self.assertEqual(len(mail.outbox), 1)

    def test_user_story_create(self):
        self.client.login(username="test2", password="test")

        post_params = {
            'priority': 3,
            'points': '10',
            'status': 'open',
            'category': '',
            'tested': False,
            'subject': 'test us',
            'description': 'test desc us',
            'finish_date': '02/02/2012',
        }

        response = self.client.post(self.project2.get_userstory_create_url(), post_params, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [('http://testserver/test2/backlog/', 302)])

        self.assertEqual(self.milestone2.user_stories.count(), 0)
        self.assertEqual(self.project2.user_stories.count(), 1)
        self.assertEqual(self.project2.tasks.count(), 0)
        self.assertEqual(len(mail.outbox), 1)

    def test_user_story_create_bad_status(self):
        self.client.login(username="test2", password="test")

        post_params = {
            'priority': 6,
            'points': '10',
            'category': '',
            'subject': 'test us',
            'description': '',
            'finish_date': '02/02/2012',
        }

        response = self.client.post(self.milestone2.get_user_story_create_url(), post_params, follow=True)
        self.assertIn("form", response.context)

        form_errors = dict(response.context['form'].errors)
        self.assertIn('description', form_errors)
        self.assertEqual(response.status_code, 200)

    def test_user_story_create_without_permissions(self):
        self.client.login(username="test2", password="test")

        post_params = {
            'priority': 6,
            'points': '10',
            'status': 'foo',
            'category': '',
            'tested': False,
            'subject': 'test us',
            'description': 'test desc us',
            'finish_date': '02/02/2012',
        }

        response = self.client.post(self.milestone1.get_user_story_create_url(), post_params, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_user_story_view(self):
        self.client.login(username="test2", password="test")

        user_story = UserStory.objects.create(
            priority = '6',
            status = 'open',
            category = '',
            tested = False,
            finish_date = self.now_date,
            subject = 'test us',
            description = 'test desc us',
            owner = self.user2,
            project = self.project2,
            milestone = self.milestone2,
        )

        response = self.client.get(user_story.get_view_url())
        self.assertEqual(response.status_code, 200)

    def test_user_story_edit(self):
        self.client.login(username="test2", password="test")

        user_story = UserStory.objects.create(
            priority = '6',
            status = 'open',
            category = '',
            tested = False,
            finish_date = self.now_date,
            subject = 'test us',
            description = 'test desc us',
            owner = self.user2,
            project = self.project2,
            milestone = self.milestone2,
        )

        post_params = {
            'priority': 6,
            'points': '10',
            'category': '',
            'subject': 'test us foo',
            'description': 'test desc us',
            'finish_date': '02/02/2012',
        }

        response = self.client.post(user_story.get_edit_url(), post_params, follow=True)
        self.assertEqual(response.status_code, 200)

        user_story = UserStory.objects.get(pk=user_story.pk)
        self.assertEqual(user_story.subject, 'test us foo')
        self.assertEqual(user_story.status, 'open')

    def test_user_story_edit_without_permission(self):
        self.client.login(username="test2", password="test")

        user_story = UserStory.objects.create(
            priority = '6',
            status = 'open',
            category = '',
            tested = False,
            finish_date = self.now_date,
            subject = 'test us',
            description = 'test desc us',
            owner = self.user1,
            project = self.project1,
            milestone = self.milestone1,
        )

        post_params = {
            'priority': 6,
            'points': '10',
            'status': 'progress',
            'category': '',
            'tested': False,
            'subject': 'test us foo',
            'description': 'test desc us',
            'finish_date': '02/02/2012',
        }

        response = self.client.post(user_story.get_edit_url(), post_params, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_assign_user_story(self):
        self.client.login(username="test2", password="test")

        user_story = UserStory.objects.create(
            priority = '6',
            status = 'open',
            category = '',
            tested = False,
            finish_date = self.now_date,
            subject = 'test us',
            description = 'test desc us',
            owner = self.user2,
            project = self.project2,
            milestone = None,
        )

        response = self.client.post(user_story.get_assign_url(), {'mid': self.milestone2.id})
        self.assertEqual(response.status_code, 200)

        user_story = UserStory.objects.get(pk=user_story.pk)
        self.assertEqual(user_story.milestone, self.milestone2)

    def test_unassign_user_story(self):
        self.client.login(username="test2", password="test")

        user_story = UserStory.objects.create(
            priority = '6',
            status = 'open',
            category = '',
            tested = False,
            finish_date = self.now_date,
            subject = 'test us',
            description = 'test desc us',
            owner = self.user2,
            project = self.project2,
            milestone = self.milestone2,
        )

        response = self.client.post(user_story.get_unassign_url(), {})
        self.assertEqual(response.status_code, 200)

        user_story = UserStory.objects.get(pk=user_story.pk)
        self.assertEqual(user_story.milestone, None)

    def test_assign_user_story_without_permissions(self):
        self.client.login(username="test2", password="test")

        user_story = UserStory.objects.create(
            priority = '6',
            status = 'open',
            category = '',
            tested = False,
            finish_date = self.now_date,
            subject = 'test us',
            description = 'test desc us',
            owner = self.user1,
            project = self.project1,
            milestone = None,
        )

        response = self.client.post(user_story.get_assign_url(), {'mid': self.milestone2.id})
        self.assertEqual(response.status_code, 403)

        user_story = UserStory.objects.get(pk=user_story.pk)
        self.assertEqual(user_story.milestone, None)

    def test_unassign_user_story_without_permissions(self):
        self.client.login(username="test2", password="test")

        user_story = UserStory.objects.create(
            priority = '6',
            status = 'open',
            category = '',
            tested = False,
            finish_date = self.now_date,
            subject = 'test us',
            description = 'test desc us',
            owner = self.user1,
            project = self.project1,
            milestone = self.milestone1,
        )

        response = self.client.post(user_story.get_unassign_url(), {})
        self.assertEqual(response.status_code, 403)

        user_story = UserStory.objects.get(pk=user_story.pk)
        self.assertEqual(user_story.milestone, self.milestone1)

    def test_user_story_delete(self):
        self.client.login(username="test2", password="test")

        user_story = UserStory.objects.create(
            priority = '6',
            status = 'open',
            category = '',
            tested = False,
            finish_date = self.now_date,
            subject = 'test us',
            description = 'test desc us',
            owner = self.user2,
            project = self.project2,
            milestone = self.milestone2,
        )

        response = self.client.post(user_story.get_delete_url(), {})
        self.assertEqual(response.status_code, 200)

        jdata = json.loads(response.content)
        self.assertIn("valid", jdata)
        self.assertTrue(jdata['valid'])
