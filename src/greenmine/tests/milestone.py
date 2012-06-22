# -*- coding: utf-8 -*-

from django.test import TestCase
from django.core import mail
from django.core.urlresolvers import reverse
import json

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
        mail.outbox = []

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
            description = "dd",
            subject = "User Story Test",
        )

        response = self.client.post(us.get_assign_url(), {'mid':milestone.id})
        self.assertEqual(response.status_code, 200)

        response = self.client.post(us.get_unassign_url())
        self.assertEqual(response.status_code, 200)

    def test_create_milestone(self):
        project = Project.objects.get(name="test1", owner=self.user1)
        project.add_user(self.user1, 'developer')
        post_params = {
            'name': 'sprint1',
            'estimated_finish': '20/01/2012',
            'estimated_start': '01/01/2012',
            'disponibility': 20,
        }
        response = self.client.post(project.get_milestone_create_url(), post_params, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [('http://testserver/test1/backlog/', 302)])

        milestone = project.milestones.get(name='sprint1')
        self.assertEqual(milestone.owner, self.user1)

        self.assertEqual(len(mail.outbox), 1)

    def test_stats_methods_0(self):
        project = Project.objects.get(name="test1", owner=self.user1)
        milestone = Milestone.objects.create(name="sprint1", project=project, owner=self.user1)

        for x in xrange(5):
            UserStory.objects.create(
                project = project,
                owner = self.user1,
                description = "test",
                subject = "User Story Test",
                milestone = milestone,
                status = 'completed',
                points = 2
            )

        self.assertEqual(milestone.total_points, '10.0')
        self.assertEqual(milestone.completed_points, '10.0')
        self.assertEqual(milestone.percentage_completed, '100.0')


    def test_stats_methods_1(self):
        project = Project.objects.get(name="test1", owner=self.user1)

        milestone = Milestone.objects.create(name="sprint1", project=project, owner=self.user1)

        UserStory.objects.create(
            project = project,
            owner = self.user1,
            description = "test",
            subject = "User Story Test",
            milestone = milestone,
            status = 'completed',
            points = 2
        )

        UserStory.objects.create(
            project = project,
            owner = self.user1,
            description = "test",
            subject = "User Story Test",
            milestone = milestone,
            status = 'open',
            points = 2
        )

        self.assertEqual(milestone.total_points, '4.0')
        self.assertEqual(milestone.completed_points, '2.0')
        self.assertEqual(milestone.percentage_completed, '50.0')

    def test_assignation_task(self):
        project = Project.objects.get(name="test1", owner=self.user1)
        project.add_user(self.user1, 'developer')

        milestone = Milestone.objects.create(name="sprint1", project=project, owner=self.user1)

        user_story  = UserStory.objects.create(
            project = project,
            owner = self.user1,
            description = "test",
            subject = "User Story Test",
            milestone = milestone,
            status = 'completed',
            points = 2
        )

        task = Task.objects.create(
            project = project,
            user_story = user_story,
            owner = self.user1,
            subject = 'Test',
            description = 'test',
            status = 'open',
        )

        self.assertEqual(task.assigned_to, None)


        url =  task.get_reassign_api_url()
        response = self.client.post(url, {'userid': self.user1.id})
        self.assertEqual(response.status_code, 200)

        jdata = json.loads(response.content)
        self.assertIn("valid", jdata)
        self.assertTrue(jdata['valid'])

        task = Task.objects.get(pk=task.pk)
        self.assertEqual(task.assigned_to, self.user1)

    def test_alteration_task(self):
        project = Project.objects.get(name="test1", owner=self.user1)
        project.add_user(self.user1, 'developer')

        milestone = Milestone.objects.create(name="sprint1", project=project, owner=self.user1)

        user_story  = UserStory.objects.create(
            project = project,
            owner = self.user1,
            description = "test",
            subject = "User Story Test",
            milestone = milestone,
            status = 'completed',
            points = 2
        )

        task = Task.objects.create(
            project = project,
            user_story = user_story,
            owner = self.user1,
            subject = 'Test',
            description = 'test',
            status = 'open',
        )

        self.assertEqual(task.status, 'open')


        url =  task.get_alter_api_url()
        response = self.client.post(url, {'status': 'progress'})
        self.assertEqual(response.status_code, 200)

        jdata = json.loads(response.content)
        self.assertIn("valid", jdata)
        self.assertTrue(jdata['valid'])

        task = Task.objects.get(pk=task.pk)
        self.assertEqual(task.status, 'progress')

        url =  task.get_alter_api_url()
        response = self.client.post(url, {'status': 'progress', 'us':''})
        self.assertEqual(response.status_code, 200)

        jdata = json.loads(response.content)
        self.assertIn("valid", jdata)
        self.assertTrue(jdata['valid'])

        task = Task.objects.get(pk=task.pk)
        self.assertEqual(task.user_story, None)



