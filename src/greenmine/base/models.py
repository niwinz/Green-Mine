# -*- coding: utf-8 -*-

from django.db.models import signals
from django.dispatch import receiver
from django.db import models

import uuid

# Centralized uuid attachment and ref generation

@receiver(signals.pre_save)
def attach_uuid_and_create_unique_ref(sender, instance, **kwargs):
    fields = sender._meta.get_all_field_names()

    # if sender class does not have uuid field.
    if "uuid" not in fields:
        return

    if not instance.uuid:
        instance.uuid = unicode(uuid.uuid1())
