# -* coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from django.utils import timezone
from django.core.files.storage import FileSystemStorage
from django.template.defaultfilters import slugify
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.contrib.auth.models import UserManager

from greenmine.core.fields import DictField, ListField
from greenmine.core.utils import iter_points

from greenmine.wiki.fields import WikiField

import datetime
import re


MARKUP_TYPE = (
    ('md', _(u'Markdown')),
    ('rst', _('Restructured Text')),
)

def ref_uniquely(project, model, field='ref'):
    """
    Returns a unique reference code based on base64 and time.
    """

    import time
    from django.utils import baseconv

    # this prevents concurrent and inconsistent references.
    time.sleep(0.1)

    new_timestamp = lambda: int("".join(str(time.time()).split(".")))
    while True:
        potential = baseconv.base62.encode(new_timestamp())
        params = {field: potential, 'project': project}
        if not model.objects.filter(**params).exists():
            return potential

        time.sleep(0.0002)


        return self.get(slug=slug)

    def can_view(self, user):
        queryset = ProjectUserRole.objects.filter(user=user)\
            .values_list('project', flat=True)
        return Project.objects.filter(pk__in=queryset)


class ExportDirectoryCache(models.Model):
    path = models.CharField(max_length=500)
    size = models.IntegerField(null=True)


# load signals
#from . import sigdispatch
