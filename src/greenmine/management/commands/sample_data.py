# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.utils import IntegrityError
from django.core import management  
import random, sys

from greenmine.models import *

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
                owner = create_user(users_counter),
                public = True,
            )
            users_counter += 1

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
                    priority = random.choice(dict(ISSUE_PRIORITY_CHOICES).keys()),
                    status = random.choice(dict(ISSUE_STATUS_CHOICES).keys()),
                    project = project,
                    type = random.choice(dict(ISSUE_TYPE_CHOICES).keys()),
                    author = random.choice(participants),
                    assigned_to = random.choice(participants),
                )
