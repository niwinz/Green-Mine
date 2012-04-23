# -*- coding: utf-8 -*-

from django.test import TestCase
from django.core import mail
from django.core.urlresolvers import reverse
from django.utils import simplejson as json

from django.contrib.auth.models import User
from ..models import *


class ProjectRelatedTests(TestCase):
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

        self.client.login(username='test', password='test')

    def tearDown(self):
        Project.objects.all().delete()
        User.objects.all().delete()
        self.client.logout()

    def test_home_projects_view(self):
        home_url = reverse('web:projects')
        response = self.client.get(home_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['projects'].count(), 0)

        self.assertIn("page", response.context)
        self.assertIn("is_paginated", response.context)

    def test_create_project(self):
        post_params = {
            'projectname': 'test-project',
            'description': 'description',
            'user_{0}'.format(self.user.id): '1',
        }

        project_create_url = reverse('web:project-create')
        response = self.client.post(project_create_url, post_params, follow=True)

        self.assertEqual(response.status_code, 200)
        jdata = json.loads(response.content)
        self.assertTrue(jdata['valid'])

    def test_normal_user_projects(self):
        """
        Permission tests, normal user only show owned projects and participant.
        """

        user1 = User.objects.create(
            username = 'test2',
            email = 'test2@test.com',
            is_active = True,
            is_staff = True,
            is_superuser = True,
            password = self.user.password,
        )

        Project.objects.bulk_create([
            Project(name='test1', description='test1', owner=self.user, slug='test1'),
            Project(name='test2', description='test2', owner=self.user, slug='test2'),
            Project(name='test3', description='test3', owner=user1, slug='test3'),
        ])

        home_url = reverse('web:projects')
        response = self.client.get(home_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['projects'].count(), 2)

    def test_project_edit(self):
        project = Project(name='test1', description='test1', owner=self.user, slug='test1')
        project.save()

        pur = ProjectUserRole.objects.create(
            user = self.user,
            project = project,
            role = Role.objects.get(pk=1),
        )

        post_params = {
            'projectname': 'test-project2',
            'description': project.description,
            'user_{0}'.format(self.user.id): '2',
        }

        project_edit_url = reverse('web:project-edit', args=[project.slug])
        response = self.client.post(project_edit_url, post_params)
        self.assertEqual(response.status_code, 200)

        jdata = json.loads(response)
        self.assertTrue(jdata['valid'])
        self.assertIn("redirect_to", jdata)

        qs = ProjectUserRole.objects.filter(
            user = self.user,
            project = project,
            role__pk = 2,
        )
        self.assertEqual(qs.count(), 1)

