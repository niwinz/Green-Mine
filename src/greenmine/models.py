# -* coding: utf-8 -*-

from django.db import models
from django.core.files.storage import FileSystemStorage
from django.template.defaultfilters import slugify
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User, UserManager

from greenmine.utils import make_repo_location, encrypt_password
from .repos.hg.api import create_repository, delete_repository
from .fields import DictField

fs = FileSystemStorage()
import datetime

ROLE_CHOICES = (
    ('developer', 'Developer'),
    ('manager', 'Project manager'),
    ('partner', 'Partner'),
    ('client', 'Client'),
)

MARKUP_TYPE = (
    ('', 'None'),
    ('markdown', 'Markdown'),
    ('rest', 'Restructured Text'),
)

ISSUE_STATUS_CHOICES = (
    ('new', 'New'),
    ('accepted', 'In progress'),
    ('fixed', 'Fixed'),
    ('invalid', 'Invalid'),
    ('wontfix', 'Wontfix'),
    ('workaround', 'Workaround'),
    ('duplicate', 'Duplicated'),
)

ISSUE_PRIORITY_CHOICES = (
    (0, 'Lower'),
    (2, 'Normal'),
    (4, 'High'),
    (6, 'Urgent'),
    (8, 'Critical'),
)

ISSUE_TYPE_CHOICES = (
    ('task', 'Task'),
    ('bug', 'Bug'),
    ('enhacement', 'Enhancement'),
)

def slugify_uniquely(value, model, slugfield="slug"):
    """
    Returns a slug on a name which is unique within a model's table
    self.slug = SlugifyUniquely(self.name, self.__class__)
    """
    suffix = 0
    potential = base = slugify(value)
    if len(potential) == 0:
        potential = 'null'
    while True:
        if suffix:
            potential = "-".join([base, str(suffix)])
        if not model.objects.filter(**{slugfield: potential}).count():
            return potential
        suffix += 1


class GenericFile(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    owner = models.ForeignKey("auth.User", related_name="files")
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to="files/msg/%Y/%m/%d", storage=fs, max_length=500, null=True, blank=True)


class GenericResponse(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    response_to = generic.GenericForeignKey('content_type', 'object_id')
    
    owner = models.ForeignKey('auth.User', related_name='myresponses')
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    attached_files = generic.GenericRelation("GenericFile")


class Profile(models.Model):
    user = models.ForeignKey("auth.User", unique=True)
    settings = DictField(default={})


class Message(models.Model):
    project = models.ForeignKey('Project', related_name='messages')
    milestone = models.ForeignKey('Milestone', related_name='messages', null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey('auth.User', related_name='mymessages')
    content = models.TextField()
    responses = generic.GenericRelation("GenericResponse")


class Project(models.Model):
    name = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField(blank=False)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)

    owner = models.ForeignKey("auth.User", related_name="projects")
    participants = models.ManyToManyField('auth.User', related_name="projects_participant", through="ProjectUserRole", null=True, blank=True)
    public = models.BooleanField(default=True)

    def __repr__(self):
        return u"<Project %s>" % (self.slug)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_uniquely(self.name, self.__class__)
        else:
            self.modified_date = datetime.datetime.now()

        super(Project, self).save(*args, **kwargs)

        if not hasattr(self, 'wiki'):
            Wiki.objects.create(project=self)


class ProjectUserRole(models.Model):
    project = models.ForeignKey("Project")
    user = models.ForeignKey("auth.User")
    role = models.CharField(max_length=100, choices=ROLE_CHOICES)

    def __repr__(self):
        return u"<Project-User-Relation-%s>" % (self.id)

    class Meta:
        unique_together = ('project', 'user')


class Wiki(models.Model):
    """ Individual project wiki system. Realation table"""
    project = models.OneToOneField('Project', related_name="wiki", null=True)
    markup = models.CharField(max_length=50, choices=MARKUP_TYPE, blank=True, default='markdown')
    
    def __repr__(self):
        return u"<Wiki %s>" % (self.id)


class WikiPage(models.Model):
    wiki = models.ForeignKey('Wiki', related_name="pages")
    owner = models.ForeignKey('auth.User', related_name="wikipages")
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    files = generic.GenericRelation("GenericFile")

    def __repr__(self):
        return u"<WikiPage %s>" % (self.slug)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_uniquely(self.name, self.__class__)
        else:
            self.modified_date = datetime.datetime.now()

        super(WikiPage, self).save(*args, **kwargs)


class Milestone(models.Model):
    name = models.CharField(max_length=200,)
    slug = models.CharField(max_length=200, unique=True)

    project = models.ForeignKey('Project', related_name="milestones")
    estimated_finish = models.DateField(null=True, default=None)
    
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    closed = models.BooleanField(default=False)

    class Meta(object):
        unique_together = ('name', 'project')
    
    def __repr__(self):
        return u"<Milestone %s>" % (self.slug)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_uniquely(self.name, self.__class__)
        else:
            self.modified_date = datetime.datetime.now()

        super(Milestone, self).save(*args, **kwargs)


class Issue(models.Model):
    priority = models.IntegerField(choices=ISSUE_TYPE_CHOICES)
    status = models.CharField(max_length=50, choices=ISSUE_STATUS_CHOICES)
    milestone = models.ForeignKey("Milestone", related_name="issues")
    project = models.ForeignKey("Project", related_name="issues")
    type = models.CharField(max_length="50", default="task")
    author = models.ForeignKey("auth.User", null=True, default=None, related_name="issues")

    priority = models.IntegerField(choices=ISSUE_PRIORITY_CHOICES, default=2)
    watchers = models.ManyToManyField("auth.User", related_name="issues_watching", 
        blank=True, null=True, default=None)
    
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    tested = models.BooleanField(default=False)
    
    subject = models.CharField(max_length=500)
    description = models.TextField()
    finish_date = models.DateTimeField(null=True, blank=True)
    files = generic.GenericRelation("GenericFile")
    responses = generic.GenericRelation("GenericResponse")

    def __repr__(self):
        return u"<Issue %s>" % (self.id)

    def save(self, *args, **kwargs):
        if self.id:
            self.modified_date = datetime.datetime.now()

        super(Issue,self).save(*args, **kwargs)


class PostSecurity(models.Model):
    """ Sirve para controlar el ratio de posts y asi evitar spam massivo. """
    remote_host = models.CharField(max_length=200, unique=True)
    last_post = models.DateTimeField(auto_now_add=True)


class Blacklist(models.Model):
    """ Sirve para poner una lista negra de ips que directamente no pueden
    acceder al sitio. """
    remote_host = models.CharField(max_length=200, unique=True)


class GSettings(models.Model):
    key = models.CharField(max_length=200, unique=True)
    value = models.TextField(blank=True, default='')

# load signals
from . import sigdispatch
