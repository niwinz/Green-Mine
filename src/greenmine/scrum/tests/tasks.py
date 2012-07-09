# -*- coding: utf-8 -*-

from django.test import TestCase
from django.core import mail
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User
from ..models import *

from greenmine.core import permissions as perms
from django.utils import timezone

import datetime
import json




class TasksTests(TestCase):
    def setUp(self):
        self.now_date = datetime.datetime.now(tz=timezone.get_default_timezone())

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

        self.user_story1 = UserStory.objects.create(
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

        self.user_story2 = UserStory.objects.create(
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
        mail.outbox = []

    def tearDown(self):
        Task.objects.all().delete()
        UserStory.objects.all().delete()
        Milestone.objects.all().delete()
        Project.objects.all().delete()
        User.objects.all().delete()

    def test_task_create(self):
        self.client.login(username="test2", password="test")

        post_params = {
            'status': 'open',
            'priority': 3,
            'subject': 'test task',
            'description': 'test desc task',
            'assigned_to': '',
            'type': 'task',
            'user_story': '',
            'milestone': self.milestone2.id,
        }

        response = self.client.post(self.milestone2.get_task_create_url(), post_params, follow=True)
        self.assertEqual(response.status_code, 200)

        jdata = json.loads(response.content)

        self.assertTrue(jdata['success'])
        self.assertIn('redirect_to', jdata)
        self.assertEqual(len(mail.outbox), 1)

    def test_task_create_without_permissions_1(self):
        self.client.login(username="test2", password="test")

        post_params = {
            'status': 'open',
            'priority': 3,
            'subject': 'test task',
            'description': 'test desc task',
            'assigned_to': '',
            'type': 'task',
            'user_story': '',
            'milestone': self.milestone2.id,
        }

        response = self.client.post(self.milestone1.get_task_create_url(), post_params, follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(mail.outbox), 0)


    def test_task_create_without_permissions_2(self):
        self.client.login(username="test2", password="test")

        post_params = {
            'status': 'open',
            'priority': 3,
            'subject': 'test task',
            'description': 'test desc task',
            'assigned_to': '',
            'type': 'task',
            'user_story': '',
            'milestone': self.milestone1.id,
        }

        response = self.client.post(self.milestone2.get_task_create_url(), post_params, follow=True)
        self.assertEqual(response.status_code, 200)

        jdata = json.loads(response.content)
        self.assertIn('errors', jdata)
        self.assertIn('form', jdata['errors'])
        self.assertIn("milestone", jdata['errors']['form'])
        self.assertEqual(len(mail.outbox), 0)

    def test_task_edit(self):
        self.client.login(username="test2", password="test")

        task = Task.objects.create(
            status = 'open',
            priority = 3,
            subject = 'test',
            description = 'test',
            assigned_to = None,
            type = 'task',
            user_story = None,
            milestone = self.milestone2,
            owner = self.user2,
            project = self.project2,
        )

        post_params = {
            'status': 'open',
            'priority': 3,
            'subject': 'test task',
            'description': 'test desc task',
            'assigned_to': self.user2.pk,
            'type': 'task',
            'user_story': '',
            'milestone': self.milestone2.id,
        }

        response = self.client.post(task.get_edit_url(), post_params, follow=True)
        self.assertEqual(response.status_code, 200)

        mod_task = Task.objects.get(pk=task.pk)
        self.assertEqual(task.priority, mod_task.priority)
        self.assertEqual(mod_task.subject, 'test task')
        self.assertEqual(len(mail.outbox), 1)

    def test_task_edit_unassignation(self):
        self.client.login(username="test2", password="test")

        task = Task.objects.create(
            status = 'open',
            priority = 3,
            subject = 'test',
            description = 'test',
            assigned_to = self.user2,
            type = 'task',
            user_story = None,
            milestone = self.milestone2,
            owner = self.user2,
            project = self.project2,
        )

        post_params = {
            'status': 'open',
            'priority': 3,
            'subject': 'test task',
            'description': 'test desc task',
            'assigned_to': '',
            'type': 'task',
            'user_story': '',
            'milestone': self.milestone2.id,
        }

        response = self.client.post(task.get_edit_url(), post_params, follow=True)
        self.assertEqual(response.status_code, 200)

        mod_task = Task.objects.get(pk=task.pk)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(mod_task.assigned_to, None)


    def test_task_delete(self):
        self.client.login(username="test2", password="test")

        task = Task.objects.create(
            status = 'open',
            priority = 3,
            subject = 'test',
            description = 'test',
            assigned_to = None,
            type = 'task',
            user_story = None,
            milestone = self.milestone2,
            owner = self.user2,
            project = self.project2,
        )

        response  = self.client.post(task.get_delete_url(), {})
        self.assertEqual(response.status_code, 200)

        jdata = json.loads(response.content)
        self.assertIn("valid", jdata)
        self.assertTrue(jdata["valid"])

    def test_task_delete_without_permissions(self):
        self.client.login(username="test2", password="test")

        task = Task.objects.create(
            status = 'open',
            priority = 3,
            subject = 'test',
            description = 'test',
            assigned_to = None,
            type = 'task',
            user_story = None,
            milestone = self.milestone1,
            owner = self.user1,
            project = self.project1,
        )

        response  = self.client.post(task.get_delete_url(), {})
        self.assertEqual(response.status_code, 403)

    def test_task_list_order_by_params(self):
        self.client.login(username="test2", password="test")

        task1 = Task.objects.create(
            status = 'progress',
            priority = 3,
            subject = 'test',
            description = 'test',
            assigned_to = None,
            type = 'task',
            user_story = None,
            milestone = self.milestone2,
            owner = self.user2,
            project = self.project2,
        )

        task2 = Task.objects.create(
            status = 'open',
            priority = 1,
            subject = 'test',
            description = 'test',
            assigned_to = None,
            type = 'bug',
            user_story = None,
            milestone = self.milestone2,
            owner = self.user2,
            project = self.project2,
        )

        response = self.client.get(self.milestone2.get_tasks_url())
        self.assertEqual(response.status_code, 200)

        tasks = response.context['tasks']
        self.assertEqual(tasks.count(), 2)

        # test initial status
        self.assertEqual(tasks[0].status, 'progress')
        self.assertEqual(tasks[1].status, 'open')

        response = self.client.get(self.milestone2.get_tasks_url() + "?order_by=status")
        self.assertEqual(response.status_code, 200)
        tasks = response.context['tasks']

        # test initial status
        self.assertEqual(tasks[0].status, 'open')
        self.assertEqual(tasks[1].status, 'progress')

    def test_tasks_filter_by(self):
        self.client.login(username="test2", password="test")

        task1 = Task.objects.create(
            status = 'progress',
            priority = 3,
            subject = 'test',
            description = 'test',
            assigned_to = None,
            type = 'task',
            user_story = None,
            milestone = self.milestone2,
            owner = self.user2,
            project = self.project2,
        )

        task2 = Task.objects.create(
            status = 'open',
            priority = 1,
            subject = 'test',
            description = 'test',
            assigned_to = None,
            type = 'bug',
            user_story = None,
            milestone = self.milestone2,
            owner = self.user2,
            project = self.project2,
        )

        response = self.client.get(self.milestone2.get_tasks_url_filter_by_task())
        self.assertEqual(response.status_code, 200)

        tasks = response.context['tasks']
        self.assertEqual(tasks.count(), 1)

        response = self.client.get(self.milestone2.get_tasks_url_filter_by_bug())
        self.assertEqual(response.status_code, 200)

        tasks = response.context['tasks']
        self.assertEqual(tasks.count(), 1)

