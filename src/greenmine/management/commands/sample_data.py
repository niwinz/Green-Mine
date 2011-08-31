# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.utils import IntegrityError
from django.core import management  
import random, sys

from greenmine.models import *

subjects = [
    "Fixing templates for Django 1.2.",
    "get_actions() does not check for 'delete_selected' in actions",
    "Experimental: modular file types",
    "Add setting to allow regular users to create folders at the root level.",
    "add tests for bulk operations",
    "create testsuite with matrix builds",
    "Lighttpd support",
    "Lighttpd x-sendfile support", 
    "Added file copying and processing of images (resizing)",
    "Exception is thrown if trying to add a folder with existing name",
    "Feature/improved image admin",
    "Support for bulk actions",
]

class Command(BaseCommand):
    @transaction.commit_on_success
    def handle(self, *args, **options):
        users_counter = 0

        def create_user(counter):
            user = User.objects.create(
                username = 'foouser%d' % (counter),
                first_name = 'foouser%d' % (counter),
                email = 'foouser%d@foodomain.com' % (counter),
            )
            return user
           
        # projects
        for x in xrange(5):
            # create project
            project = Project.objects.create(
                name = 'FooProject%s' % (x),
                description = 'Foo project description %s' % (x),
                owner = random.choice(list(User.objects.all())),
                public = True,
            )

            # add owner to participants list
            ProjectUserRole.objects.create(
                project = project,
                user = project.owner,
                role = 'developer'
            )
            
            # add random participants to project
            participants = []
            for t in xrange(random.randint(3, 12)):
                participant = create_user(users_counter)
                participants.append(participant)
                ProjectUserRole.objects.create(
                    project = project,
                    user = participant,
                    role = random.choice(dict(ROLE_CHOICES).keys()),
                )
                users_counter += 1
            
            # create random milestones
            for y in xrange(3):
                milestone = Milestone.objects.create(
                    project = project,
                    name = 'Sprint%s' % (y),
                )
                
                # create issues asociated to milestones
                for z in xrange(random.randint(15, 50)):
                    issue = Issue.objects.create(
                        subject = random.choice(subjects),
                        priority = random.choice(dict(ISSUE_PRIORITY_CHOICES).keys()),
                        status = random.choice(dict(ISSUE_STATUS_CHOICES).keys()),
                        project = project,
                        type = random.choice(dict(ISSUE_TYPE_CHOICES).keys()),
                        author = random.choice(participants),
                        assigned_to = random.choice(participants),
                        milestone = milestone,
                        parent = None,
                    )
            # created unassociated issues.
            for y in xrange(20):
                issue = Issue.objects.create(
                    subject = random.choice(subjects),
                    priority = random.choice(dict(ISSUE_PRIORITY_CHOICES).keys()),
                    status = random.choice(dict(ISSUE_STATUS_CHOICES).keys()),
                    project = project,
                    type = random.choice(dict(ISSUE_TYPE_CHOICES).keys()),
                    author = random.choice(participants),
                    assigned_to = random.choice(participants),
                )
