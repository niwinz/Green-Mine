"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test import Client

from django.utils import simplejson
from django.utils import unittest

from greenmine.models import *
from greenmine.utils import encrypt_password

import logging, os.path
log = logging.getLogger('greenmine')


project_root = os.path.dirname(os.path.join(os.path.realpath(__file__)))

class UserTest(unittest.TestCase):
    def setUp(self):
        self.user = User.objects.create(username='andrei', password=encrypt_password(u'123123'), superuser=True)
        self.client = Client()
        response = self.client.post("/api/login", {'username':u'andrei', 'password':u'123123'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(simplejson.loads(response.content)['valid'], True)
    
    def tearDown(self):
        self.user.delete()

    def test_user_view_exists(self):
        response = self.client.get("/api/user?username=andrei")
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertIn("object", data)

    def test_invalid_login(self):
        response = self.client.post('/api/login', {'username': 'andrei', 'password': 'antoukh'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(simplejson.loads(response.content)['valid'], False)

    def test_user_view_notexists(self):
        response = self.client.get("/api/user?username=pepe")
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertNotIn("object", data)
        self.assertNotEqual(len(data['errors']), 0)

    def test_response_and_modification(self):
        response = self.client.post('/api/user/edit', {'description':'Hola'})
        self.assertEqual(response.status_code, 200)
        
        data = simplejson.loads(response.content)
        self.assertEqual(data['id'], self.user.id)
        self.assertEqual(User.objects.get(id=data['id']).description, u'Hola')


    def test_upload_profile_photo(self):
        response = self.client.post('/api/user/edit', 
            {'photo': open(os.path.join(project_root, 'static', 'test.png'), 'rb')})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertEqual(data['id'], self.user.id)
        self.assertTrue(User.objects.get(pk=data['id']).photo)
    
    def test_project_create_superuser(self):
        response = self.client.post('/api/project/create', {'name':'test project'})
        
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertNotEqual(data['id'], None)
        self.assertTrue(Project.objects.filter(pk=data['id']).exists())
        self.assertIn("project", data)

    def test_project_duplicate(self):
        self.user.superuser = False
        self.user.save()

        response = self.client.post('/api/project/create', {'name':'test project', 'role':'developer'})
        response = self.client.post('/api/project/create', {'name':'test project', 'role':'developer'})

        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)

        self.assertNotIn("project", data)
        self.assertNotEqual(len(data['errors']), 0)


    def test_project_create_invalid_role(self):
        response = self.client.post('/api/project/create', {'name':'test project', 'role':'foo'})
        print "test_project_create_invalid_role", response.content
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)

        self.assertNotIn("project", data)
        self.assertNotEqual(len(data['errors']), 0)


