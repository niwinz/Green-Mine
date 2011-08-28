# -* coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.files.storage import FileSystemStorage
from django.template.defaultfilters import slugify
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User, UserManager

#from greenmine.utils import make_repo_location, encrypt_password
#from .repos.hg.api import create_repository, delete_repository
from greenmine.fields import DictField

import datetime

ROLE_CHOICES = (
    ('observer', _(u'Observer')),
    ('developer', _(u'Developer')),
    ('manager', _(u'Project manager')),
    ('partner', _(u'Partner')),
    ('client', _(u'Client')),
)

MARKUP_TYPE = (
    ('', 'None'),
    ('markdown', _(u'Markdown')),
    ('rest', _('Restructured Text')),
)

ISSUE_STATUS_CHOICES = (
    ('new', _(u'New')),
    ('accepted', _(u'In progress')),
    ('fixed', _(u'Fixed')),
    ('invalid', _(u'Invalid')),
    ('wontfix', _(u'Wontfix')),
    ('workaround', _(u'Workaround')),
    ('duplicate', _(u'Duplicated')),
)

ISSUE_PRIORITY_CHOICES = (
    (1, _(u'Lower')),
    (2, _(u'Normal')),
    (4, _(u'High')),
    (6, _(u'Urgent')),
    (8, _(u'Critical')),
)

ISSUE_TYPE_CHOICES = (
    ('task', _(u'Task')),
    ('bug', _(u'Bug')),
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


def ref_uniquely(model, field='ref'):
    """
    Returns a unique reference code based on base64 and time.
    """

    import time, baseconv
    potential = baseconv.base62.encode(int(time.time()))
    while True:
        if not model.objects.filter(**{field: potential}).exists():
            return potential
        time.sleep(0.6)


class GenericFile(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    owner = models.ForeignKey("auth.User", related_name="files")
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to="files/msg/%Y/%m/%d", max_length=500, null=True, blank=True)


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
    description = models.TextField(blank=True)
    photo = models.FileField(upload_to="files/msg/%Y/%m/%d", max_length=500, null=True, blank=True)
    settings = DictField(default={})


class Message(models.Model):
    project = models.ForeignKey('Project', related_name='messages')
    milestone = models.ForeignKey('Milestone', related_name='messages', null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey('auth.User', related_name='mymessages')
    content = models.TextField()
    responses = generic.GenericRelation("GenericResponse")


class ProjectManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)

class Project(models.Model):
    name = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField(blank=False)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)

    owner = models.ForeignKey("auth.User", related_name="projects")
    participants = models.ManyToManyField('auth.User', related_name="projects_participant", through="ProjectUserRole", null=True, blank=True)
    public = models.BooleanField(default=True)

    objects = ProjectManager()

    def natural_key(self):
        return (self.slug,)

    def __repr__(self):
        return u"<Project %s>" % (self.slug)

    @models.permalink
    def get_dashboard_url(self):
        return ('web:project', (), {'slug':self.slug})

    @models.permalink
    def get_unasigned_tasks_api_url(self):
        return ('api:unasigned-tasks-for-poject', (), {'pslug':self.slug})

    @models.permalink
    def get_delete_api_url(self):
        return ('api:project-delete', (), {'pslug': self.slug})

    @models.permalink
    def get_milestone_create_api_url(self):
        return ('api:project-milestone-create', (), {'pslug': self.slug})

    @models.permalink
    def get_issue_create_api_url(self):
        return ('api:project-issue-create', (), {'pslug': self.slug})

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


class MilestoneManager(models.Manager):
    def get_by_natural_key(self, name, project):
        return self.get(name=name, project__slug=project)


class Milestone(models.Model):
    name = models.CharField(max_length=200,)
    project = models.ForeignKey('Project', related_name="milestones")
    estimated_finish = models.DateField(null=True, default=None)
    
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    closed = models.BooleanField(default=False)

    objects = MilestoneManager()

    @models.permalink
    def get_tasks_for_milestone_api_url(self):
        return ('api:tasks-for-milestone', (), 
            {'pslug':self.project.slug, 'mid':self.id})

    class Meta(object):
        unique_together = ('name', 'project')

    def natural_key(self):
        return (self.name,) + self.project.natural_key()

    natural_key.dependencies = ['greenmine.Project']
    
    def __repr__(self):
        return u"<Milestone %s>" % (self.slug)

    def save(self, *args, **kwargs):
        if self.id:
            self.modified_date = datetime.datetime.now()

        super(Milestone, self).save(*args, **kwargs)


class Issue(models.Model):
    ref = models.CharField(max_length=200, unique=True, db_index=True, null=True, default=None)
    status = models.CharField(max_length=50, choices=ISSUE_STATUS_CHOICES)
    milestone = models.ForeignKey("Milestone", related_name="issues", null=True, default=None)
    project = models.ForeignKey("Project", related_name="issues")
    type = models.CharField(max_length="50", default="task", choices=ISSUE_TYPE_CHOICES)
    author = models.ForeignKey("auth.User", null=True, default=None, related_name="issues")

    priority = models.IntegerField(choices=ISSUE_PRIORITY_CHOICES, default=2)
    watchers = models.ManyToManyField("auth.User", related_name="issues_watchin", 
        blank=True, null=True, default=None)
    
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    tested = models.BooleanField(default=False)
    
    subject = models.CharField(max_length=500)
    description = models.TextField()
    finish_date = models.DateTimeField(null=True, blank=True)
    files = generic.GenericRelation("GenericFile")
    responses = generic.GenericRelation("GenericResponse")

    assigned_to = models.ForeignKey('auth.User', related_name='issues_assigned_to_me', null=True, default=None)
    parent = models.ForeignKey('self', related_name='subtasks', null=True, default=None)

    def __repr__(self):
        return u"<Issue %s>" % (self.id)

    def save(self, *args, **kwargs):
        if self.id:
            self.modified_date = datetime.datetime.now()
        if not self.ref:
            self.ref = ref_uniquely(self.__class__)

        super(Issue,self).save(*args, **kwargs)

    @models.permalink
    def get_edit_api_url(self):
        return ('api:issue-edit', (), {'pslug': self.project.slug, 'issueid': self.id})


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
