# -*- coding: utf-8 -*-

from django.test import TestCase
from django.core import mail
from django.core.urlresolvers import reverse
from django.utils import simplejson as json

from django.contrib.auth.models import User
from ..models import *

from greenmine import permissions as perms
from django.utils import timezone
import datetime


class SimplePermissionMethodsTest(TestCase):
    def test_has_permission(self):
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

        self.assertTrue(perms.has_perm(user, project, "project", "view"))
        self.assertTrue(perms.has_perm(user, project, "task", "edit"))

        project.delete()
        user.delete()
        pur.delete()

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
        home_url = reverse('web:projects')
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

        project_create_url = reverse('web:project-create')
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

        project_create_url = reverse('web:project-create')
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

        home_url = reverse('web:projects')
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

        project_edit_url = reverse('web:project-edit', args=[project.slug])
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
        
        response = self.client.get(reverse('web:project-edit', args=[project.slug]), follow=True)

        # expected one message
        self.assertEqual(len(response.context['messages']), 1)
        
        # expected redirect
        self.assertEqual(response.redirect_chain, [('http://testserver/', 302)])


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
        }


        response = self.client.post(self.project1.get_milestone_create_url(), post_params)
        self.assertEqual(response.status_code, 403)

    def test_create_milestone_without_permissions_superuser(self):
        self.client.login(username="test1", password="test")

        post_params = {
            'name': 'test milestone',
            'estimated_finish': '02/02/2012',
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
        self.assertEqual(self.project2.tasks.count(), 1)

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
        self.assertEqual(self.project2.tasks.count(), 1)

    def test_user_story_create_bad_status(self):
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

        response = self.client.post(self.milestone2.get_user_story_create_url(), post_params, follow=True)
        self.assertIn("form", response.context)
        
        form_errors = dict(response.context['form'].errors)
        self.assertIn('status', form_errors)
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
            'status': 'progress',
            'category': '',
            'tested': False,
            'subject': 'test us foo',
            'description': 'test desc us',
            'finish_date': '02/02/2012',
        }
        
        response = self.client.post(user_story.get_edit_url(), post_params, follow=True)
        self.assertEqual(response.status_code, 200)

        user_story = UserStory.objects.get(pk=user_story.pk)
        self.assertEqual(user_story.subject, 'test us foo')
        self.assertEqual(user_story.status, 'progress')

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
        self.assertEqual(response.redirect_chain, [('http://testserver/test2/milestone/2/task/list/', 302)])

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

        form_errors = dict(response.context['form'].errors)
        self.assertIn("milestone", form_errors)

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
            'assigned_to': '',
            'type': 'task',
            'user_story': '',
            'milestone': self.milestone2.id,
        }

        response = self.client.post(task.get_edit_url(), post_params, follow=True)
        self.assertEqual(response.status_code, 200)

        mod_task = Task.objects.get(pk=task.pk)
        self.assertEqual(task.priority, mod_task.priority)
        self.assertEqual(mod_task.subject, 'test task')

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
        self.assertEqual(tasks.count(), 3)

        # test initial status
        self.assertEqual(tasks[0].status, 'open')
        self.assertEqual(tasks[1].status, 'progress')
        self.assertEqual(tasks[2].status, 'open')

        response = self.client.get(self.milestone2.get_tasks_url() + "?order_by=status")
        self.assertEqual(response.status_code, 200)
        tasks = response.context['tasks']

        # test initial status
        self.assertEqual(tasks[0].status, 'open')
        self.assertEqual(tasks[1].status, 'open')
        self.assertEqual(tasks[2].status, 'progress')

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
        self.assertEqual(tasks.count(), 2)
        
        response = self.client.get(self.milestone2.get_tasks_url_filter_by_bug())
        self.assertEqual(response.status_code, 200)

        tasks = response.context['tasks']
        self.assertEqual(tasks.count(), 1)

