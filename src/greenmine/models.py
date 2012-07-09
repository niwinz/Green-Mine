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



class TemporalFile(models.Model):
    attached_file = models.FileField(upload_to="temporal_files",
        max_length=1000, null=True, blank=True)

    owner = models.ForeignKey('auth.User', related_name='tmpfiles')
    created_date = models.DateTimeField(auto_now_add=True)


class Document(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, max_length=200, blank=True)
    description = WikiField(blank=True)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)

    project = models.ForeignKey('Project', related_name='documents')
    owner = models.ForeignKey('auth.User', related_name='documents')
    attached_file = models.FileField(upload_to="documents",
        max_length=1000, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_uniquely(self.title, self.__class__)
        super(Document, self).save(*args, **kwargs)

    @models.permalink
    def get_delete_url(self):
        return ('documents-delete', (),
            {'pslug': self.project.slug, 'docid': self.pk})


class ExportDirectoryCache(models.Model):
    path = models.CharField(max_length=500)
    size = models.IntegerField(null=True)


# load signals
#from . import sigdispatch
