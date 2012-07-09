# -*- coding: utf-8 -*-

from django.db import models

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext


class Role(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)

    project_view = models.BooleanField(default=True)
    project_edit = models.BooleanField(default=False)
    project_delete = models.BooleanField(default=False)
    userstory_view = models.BooleanField(default=True)
    userstory_create = models.BooleanField(default=False)
    userstory_edit = models.BooleanField(default=False)
    userstory_delete = models.BooleanField(default=False)
    milestone_view = models.BooleanField(default=True)
    milestone_create = models.BooleanField(default=False)
    milestone_edit = models.BooleanField(default=False)
    milestone_delete = models.BooleanField(default=False)
    task_view = models.BooleanField(default=True)
    task_create = models.BooleanField(default=False)
    task_edit = models.BooleanField(default=False)
    task_delete = models.BooleanField(default=False)
    wiki_view = models.BooleanField(default=True)
    wiki_create = models.BooleanField(default=False)
    wiki_edit = models.BooleanField(default=False)
    wiki_delete = models.BooleanField(default=False)
    question_view = models.BooleanField(default=True)
    question_create = models.BooleanField(default=True)
    question_edit = models.BooleanField(default=True)
    question_delete = models.BooleanField(default=False)
    document_view = models.BooleanField(default=True)
    document_create = models.BooleanField(default=True)
    document_edit = models.BooleanField(default=True)
    document_delete = models.BooleanField(default=True)
