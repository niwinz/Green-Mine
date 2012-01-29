# -*- coding: utf-8 -*-

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from greenmine.models import Profile, UserStory, Task
import datetime

@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """Create void user profile if instance is a new user. """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=UserStory)
def us_post_save(sender, instance, created, **kwargs):
    if created:
        task = Task.objects.create(
            subject = instance.subject,
            description = instance.description,
            owner = instance.owner,
            milestone = instance.milestone,
            project = instance.project,
            user_story = instance,
        )

@receiver(post_save, sender=Task)
def task_post_save(sender, instance, created, **kwargs):
    if instance.user_story:
        instance.user_story.modified_date = datetime.datetime.now()
        instance.user_story.save()

