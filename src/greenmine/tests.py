"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.utils import simplejson as json
from django.core.urlresolvers import reverse
from greenmine import models


class LoginApiTest(TestCase):
    def test_api_login_ajax(self):
        res = self.client.post(reverse('api:login'), 
            {'username':'andrei', 'password':'123123'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(res.status_code, 200)


class UserListApiTest(TestCase):
    def test_user_list(self):
        res = self.client.get(reverse('api:user-list'))
        self.assertEqual(res.status_code, 200)

        data = json.loads(res.content)
        self.assertTrue(data['valid'])
        self.assertEqual(len(data['list']), 0)

    def test_user_list_with_term(self):
        res = self.client.get(reverse('api:user-list') + '?term=andrei')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)
        self.assertTrue(data['valid'])
        self.assertEqual(len(data['list']), 1)
        self.assertEqual(data['list'][0]['id'], 1)


class MilestoneApiTest(TestCase):
    def setUp(self):
        self.user1 = models.User.objects.get(username='andrei')
        self.user2 = models.User.objects.exclude(username='andrei')[0]
        self.project = models.Project.objects.create(
            owner = self.user1,
            name = 'test',
            description = 'test-description',
        )
        self.milestone = models.Milestone.objects.create(
            name = 'test',
            project = self.project,
        )
        
    def tearDown(self):
        self.project.delete()

    def test_tasks_for_milestone(self):
        res = self.client.get(self.milestone.get_tasks_for_milestone_api_url())
        self.assertEqual(res.status_code, 200)

        data = json.loads(res.content)
        self.assertTrue(data['valid'])
        self.assertEqual(len(data['tasks']), 0)

    def test_tasks_for_milestone_with_tasks(self):
        issue1 = models.Issue.objects.create(
            project = self.project,
            status = 'new',
            milestone = self.milestone,
            author = self.user1,
            subject = 'testissue',
            description = 'testissue-description',
        )
        issue2 = models.Issue.objects.create(
            project = self.project,
            status = 'new',
            author = self.user1,
            subject = 'testissue',
            description = 'testissue-description',
        )
        res = self.client.get(self.milestone.get_tasks_for_milestone_api_url())
        self.assertEqual(res.status_code, 200)
        
        data = json.loads(res.content)

        self.assertTrue(data['valid'])
        self.assertEqual(len(data['tasks']), 1)

        res = self.client.get(self.project.get_unasigned_tasks_api_url())
        self.assertEqual(res.status_code, 200)

        data = json.loads(res.content)
        self.assertTrue(data['valid'])
        self.assertEqual(len(data['tasks']), 1)


        issue1.delete()
        issue2.delete()


