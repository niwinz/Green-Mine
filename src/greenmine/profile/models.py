# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from django.utils import timezone
from django.core.files.storage import FileSystemStorage
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from greenmine.core.fields import DictField, ListField
from greenmine.wiki.fields import WikiField
from greenmine.core.utils import iter_points

import datetime
import re


class Profile(models.Model):
    user = models.OneToOneField("auth.User", related_name='profile')
    description = WikiField(blank=True)
    photo = models.FileField(upload_to="files/msg",
        max_length=500, null=True, blank=True)

    default_language = models.CharField(max_length=20,
        null=True, blank=True, default=None)
    default_timezone = models.CharField(max_length=20,
        null=True, blank=True, default=None)
    token = models.CharField(max_length=200, unique=True,
        null=True, blank=True, default=None)


from . import sigdispatch
