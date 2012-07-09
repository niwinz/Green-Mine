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

from greenmine.core.fields import DictField, ListField, WikiField
from greenmine.core.utils import iter_points

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


class Question(models.Model):
    subject = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, max_length=250, blank=True)
    content = WikiField(blank=True)
    closed = models.BooleanField(default=False)
    attached_file = models.FileField(upload_to="messages",
        max_length=500, null=True, blank=True)

    project = models.ForeignKey('Project', related_name='questions')
    milestone = models.ForeignKey('Milestone', related_name='questions',
        null=True, default=None, blank=True)

    assigned_to = models.ForeignKey("auth.User")
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey('auth.User', related_name='questions')


    watchers = models.ManyToManyField('auth.User',
        related_name='question_watch', null=True, blank=True)

    @models.permalink
    def get_view_url(self):
        return ('questions-view', (),
            {'pslug': self.project.slug, 'qslug': self.slug})

    @models.permalink
    def get_edit_url(self):
        return ('questions-edit', (),
            {'pslug': self.project.slug, 'qslug': self.slug})

    @models.permalink
    def get_delete_url(self):
        return ('questions-delete', (),
            {'pslug': self.project.slug, 'qslug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_uniquely(self.subject, self.__class__)
        super(Question, self).save(*args, **kwargs)


class QuestionResponse(models.Model):
    content = WikiField()
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    attached_file = models.FileField(upload_to="messages",
        max_length=500, null=True, blank=True)

    question = models.ForeignKey('Question', related_name='responses')
    owner = models.ForeignKey('auth.User', related_name='questions_responses')


class WikiPage(models.Model):
    project = models.ForeignKey('Project', related_name='wiki_pages')
    slug = models.SlugField(max_length=500, db_index=True)
    content = WikiField(blank=False, null=True)
    owner = models.ForeignKey("auth.User", related_name="wiki_pages", null=True)

    watchers = models.ManyToManyField('auth.User',
        related_name='wikipage_watchers', null=True)

    created_date = models.DateTimeField(auto_now_add=True)

    @models.permalink
    def get_view_url(self):
        return ('wiki-page', (),
            {'pslug': self.project.slug, 'wslug': self.slug})

    @models.permalink
    def get_edit_url(self):
        return ('wiki-page-edit', (),
            {'pslug': self.project.slug, 'wslug': self.slug})

    @models.permalink
    def get_delete_url(self):
        return ('wiki-page-delete', (),
            {'pslug': self.project.slug, 'wslug': self.slug})

    @models.permalink
    def get_history_view_url(self):
        return ('wiki-page-history', (),
            {'pslug': self.project.slug, 'wslug': self.slug})



class WikiPageHistory(models.Model):
    wikipage = models.ForeignKey("WikiPage", related_name="history_entries")
    content = WikiField(blank=True, null=True)
    created_date = models.DateTimeField()
    owner = models.ForeignKey("auth.User", related_name="wiki_page_historys")

    # TODO: fix this permalink. this implementation is bad for performance.

    @models.permalink
    def get_history_view_url(self):
        return ('wiki-page-history-view', (),
            {'pslug': self.wikipage.project.slug, 'wslug': self.wikipage.slug, 'hpk': self.pk})


class WikiPageAttachment(models.Model):
    wikipage = models.ForeignKey('WikiPage', related_name='attachments')
    owner = models.ForeignKey("auth.User", related_name="wikifiles")
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    attached_file = models.FileField(upload_to="files/wiki",
        max_length=500, null=True, blank=True)


class ExportDirectoryCache(models.Model):
    path = models.CharField(max_length=500)
    size = models.IntegerField(null=True)


# load signals
from . import sigdispatch
