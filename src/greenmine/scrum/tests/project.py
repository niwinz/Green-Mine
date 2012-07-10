# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core import mail
from django.test import TestCase
from django.utils import timezone

from ..models import Project, ProjectUserRole
from ...core import permissions as perms

import datetime
import json


class SimplePermissionMethodsTest(TestCase):
    fixtures = ['initial_data']

    def test_has_permission(self):
        user = User.objects.create(
            username = 'test',
            email = 'test@test.com',
            is_active = True,
            is_staff = False,
            is_superuser = False,
        )

        project = Project.objects.create(name='test1', description='test1', owner=user, slug='test1')
        project.add_user(user, "developer")

        self.assertTrue(perms.has_perm(user, project, "project", "view"))
        self.assertTrue(perms.has_perm(user, project, "task", "edit"))

        project.delete()
        user.delete()

    def test_has_multiple_permissions(self):
        user = User.objects.create(
            username = 'test',
            email = 'test@test.com',
            is_active = True,
            is_staff = False,
            is_superuser = False,
        )

        project = Project.objects.create(name='test1', description='test1', owner=user, slug='test1')
        role = perms.get_role('developer')

        pur = ProjectUserRole.objects.create(
            project = project,
            user = user,
            role = role,
        )

        self.assertTrue(perms.has_perms(user, project, [
            ('project', 'view'),
            ('milestone', 'view'),
            ('userstory', 'view'),
        ]))

    def tearDown(self):
        ProjectUserRole.objects.all().delete()
        Project.objects.all().delete()
        User.objects.all().delete()


class ProjectRelatedTests(TestCase):
    fixtures = ['initial_data']

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
        ProjectUserRole.objects.all().delete()
        Project.objects.all().delete()
        User.objects.all().delete()
        self.client.logout()

    def test_parse_ustext(self):
        text = """
        Note that you’ll need to convert before you make any changes; South detects changes by comparing
        against the frozen state of the last migration, so it cannot detect changes from before you converted
        to using South.

        Task: Foo task.
        Task: Foo2 task.
        """

        project = Project.objects.create(name='test1', description='test1', owner=self.user, slug='test1')
        extras_instance = project.get_extras()

        tasks = list(extras_instance.parse_ustext(text))
        self.assertEqual(len(tasks), 2)

    def test_project_extras(self):
        project = Project.objects.create(name='test1', description='test1', owner=self.user, slug='test1')
        self.assertNotEqual(project.get_extras(), None)

        Project.objects.bulk_create([
            Project(name='test2', description='test1', owner=self.user, slug='test2'),
            Project(name='test3', description='test2', owner=self.user, slug='test3'),
        ])

        project = Project.objects.get(name='test2')
        self.assertEqual(project.extras, None)
        self.assertNotEqual(project.get_extras(), None)

        project = Project.objects.get(name='test2')
        self.assertNotEqual(project.extras, None)

    def test_permission_on_general_settings(self):
        superuser = User.objects.create(
            username = 'test2',
            email = 'test2@test.com',
            is_active = True,
            is_superuser = True,
        )

        project1 = Project(name='test1', description='test1', owner=self.user, slug='test1')
        project1.save()

        project2 = Project(name='test2', description='test2', owner=superuser, slug='test2')
        project2.save()

        project1.add_user(self.user, 'developer')
        project2.add_user(superuser, 'developer')

        response = self.client.get(project1.get_general_settings_url())
        self.assertEqual(response.status_code, 200)

        response = self.client.get(project2.get_general_settings_url())
        self.assertEqual(response.status_code, 403)

    def test_home_projects_view(self):
        home_url = reverse('projects')
        response = self.client.get(home_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['projects'].count(), 0)

        self.assertIn("page", response.context)
        self.assertIn("is_paginated", response.context)

    def test_create_project(self):
        post_params = {
            'name': 'test-project',
            'description': 'description',
            'user_{0}'.format(self.user.id): '1',
        }

        project_create_url = reverse('project-create')
        response = self.client.post(project_create_url, post_params, follow=True)

        self.assertEqual(response.status_code, 200)
        jdata = json.loads(response.content)
        self.assertTrue(jdata['valid'])

    def test_create_duplicate_project(self):
        self.test_create_project()

        post_params = {
            'name': 'test-project',
            'description': 'description',
            'user_{0}'.format(self.user.id): '1',
        }

        project_create_url = reverse('project-create')
        response = self.client.post(project_create_url, post_params, follow=True)

        self.assertEqual(response.status_code, 200)
        jdata = json.loads(response.content)
        self.assertFalse(jdata['valid'])

    def test_delete_project(self):
        self.test_create_project()

        project = Project.objects.get(name='test-project')

        response = self.client.post(project.get_delete_url(), {})
        self.assertEqual(response.status_code, 200)

        jdata = json.loads(response.content)
        self.assertIn("valid", jdata)
        self.assertTrue(jdata['valid'])

        self.assertEqual(Project.objects.all().count(), 0)

    def test_normal_user_projects(self):
        """
        Permission tests, normal user only show
        owned projects and participant.
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

        home_url = reverse('projects')
        response = self.client.get(home_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['projects'].count(), 2)

    def test_project_edit(self):
        project = Project(name='test1', description='test1', owner=self.user, slug='test1')
        project.save()

        project.add_user(self.user, 'developer')

        post_params = {
            'name': 'test-project2',
            'description': project.description,
            'user_{0}'.format(self.user.id): '2',
        }

        project_edit_url = reverse('project-edit', args=[project.slug])
        response = self.client.post(project_edit_url, post_params)
        self.assertEqual(response.status_code, 200)

        jdata = json.loads(response.content)
        self.assertTrue(jdata['valid'])
        self.assertIn("redirect_to", jdata)

        qs = ProjectUserRole.objects.filter(
            user = self.user,
            project = project,
            role__pk = 2,
        )
        self.assertEqual(qs.count(), 1)

    def test_get_project_edit_page_without_permision(self):
        """
        Test make GET request on a project edit form with
        some user with developer role, but without ownership of project.
        FIXME: this is unfinished test. Project edit/create form need big refactor.
        """

        user1 = User.objects.create(
            username = 'test2',
            email = 'test2@test.com',
            is_active = True,
            is_staff = True,
            is_superuser = True,
            password = self.user.password,
        )

        project = Project(name='test1', description='test1', owner=user1, slug='test1')
        project.save()

        project.add_user(self.user, 'developer')

        response = self.client.get(reverse('project-edit', args=[project.slug]), follow=True)

        # expected one message
        self.assertEqual(len(response.context['messages']), 1)

        # expected redirect
        self.assertEqual(response.redirect_chain, [('http://testserver/', 302)])
