# -*- coding: utf-8 -*-

from django.test import TestCase
from django.core import mail
from django.core.urlresolvers import reverse
from django.utils import simplejson as json

from django.contrib.auth.models import User
from ..models import *

from greenmine.permissions import get_role, has_permission
from greenmine import permissions as perms


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


        self.assertTrue(perms.has_permission(user, project, "project", "view"))
        self.assertTrue(perms.has_permission(user, project, "task", "edit"))




