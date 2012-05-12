# -*- coding: utf-8 -*-

from django.test import TestCase
from django.core import mail
from django.core.urlresolvers import reverse
import json

from django.contrib.auth.models import User
from ..models import *


class QuestionsRelatedTests(TestCase):
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
        Question.objects.all().delete()
        Project.objects.all().delete()
        User.objects.all().delete()
        self.client.logout()
        mail.outbox = []

    def test_create_question(self):
        project = Project.objects.get(name='test1')
        project.add_user(self.user1, "developer")
        project.add_user(self.user2, "developer")

        url = project.get_questions_create_url()

        post_params = {
            'subject': 'test',
            'content': 'test',
            'closed': False,
            'assigned_to': self.user1.id,
        }

        response = self.client.post(url, post_params, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [('http://testserver/test1/questions/test/view/', 302)])

        questions = Question.objects.filter(project=project)
        self.assertEqual(questions.count(), 1)

        question = questions[0]
        self.assertEqual(question.owner, self.user1)
        self.assertEqual(question.watchers.all().count(), 0)
        self.assertEqual(len(mail.outbox), 2)

    def test_post_responses(self):
        project = Project.objects.get(name='test1')
        project.add_user(self.user1, "developer")

        question = Question(
            project = project,
            owner = self.user1,
            subject = 'test',
            content = 'test',
            closed = False,
            assigned_to = self.user2,
        )

        question.save()

        url = question.get_view_url()

        post_params = {
            'content': 'response text',
        }

        response = self.client.post(url, post_params, follow=True)
        self.assertEqual(response.redirect_chain, [('http://testserver/test1/questions/test/view/', 302)])
        self.assertEqual(response.status_code, 200)

        self.assertIn("question", response.context)
        self.assertEqual(response.context['question'].responses.all().count(), 1)

    def test_create_question_view(self):
        project = Project.objects.get(name='test1')
        project.add_user(self.user1, "developer")

        url = project.get_questions_create_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_question_view(self):
        project = Project.objects.get(name='test1')
        project.add_user(self.user1, "developer")

        question = Question(
            project = project,
            owner = self.user1,
            subject = 'test',
            content = 'test',
            closed = False,
            assigned_to = self.user2,
        )

        question.save()

        response = self.client.get(question.get_view_url())
        self.assertEqual(response.status_code, 200)
