# -*- coding: utf-8 -*-

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from greenmine.models import Profile, Issue
from copy import deepcopy
import datetime

@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """Create void user profile if instance is a new user. """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=Issue)
def issue_post_save(sender, instance, created, **kwargs):
    if not instance.parent and created:
        new_instance = deepcopy(instance)
        new_instance.id = None
        new_instance.ref = None
        new_instance.parent = instance
        new_instance.save()

        instance.modified_date = datetime.datetime.now()
        instance.save()
