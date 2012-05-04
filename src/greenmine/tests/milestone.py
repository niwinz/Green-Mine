# -*- coding: utf-8 -*-

from django.test import TestCase
from django.core import mail
from django.core.urlresolvers import reverse
from django.utils import simplejson as json

from django.contrib.auth.models import User
from ..models import *


class MilestoneRelatedTests(TestCase):
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
        Task.objects.all().delete()
        UserStory.objects.all().delete()
        Milestone.objects.all().delete()
        Project.objects.all().delete()
        User.objects.all().delete()
        self.client.logout()

    def test_assign_user_story(self):
        project = Project.objects.get(name="test1", owner=self.user1)
        milestone = Milestone.objects.create(name="sprint1", project=project, owner=self.user1)

        us = UserStory.objects.create(
            milestone = None,
            project = project,
            owner = self.user1,
            description = "test",
            subject = "User Story Test",
        )

        response = self.client.post(us.get_assign_url(), {'mid':milestone.id})
        self.assertEqual(response.status_code, 200)

        self.assertEqual(us.tasks.count(), 1)
        self.assertEqual(milestone.tasks.count(), 1)
        self.assertEqual(project.tasks.count(), 1)

        response = self.client.post(us.get_unassign_url())
        self.assertEqual(response.status_code, 200)

        self.assertEqual(us.tasks.count(), 1)
        self.assertEqual(milestone.tasks.count(), 0)
        self.assertEqual(project.tasks.count(), 1)

    def test_create_milestone(self):
        project = Project.objects.get(name="test1", owner=self.user1)
        post_params = {
            'name': 'sprint1',
            'estimated_finish': '01/01/2012',
        }
        response = self.client.post(project.get_milestone_create_url(), post_params, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [('http://testserver/test1/backlog/', 302)])

        milestone = project.milestones.get(name='sprint1')
        self.assertEqual(milestone.owner, self.user1)
