# -*- coding: utf-8 -*-

from django.db import models
from django.core.files.storage import FileSystemStorage
from django.template.defaultfilters import slugify

from .repos.hg.api import create_repository, delete_repository
from .fields import DictField

from greenmine.utils import make_repo_location, encrypt_password

fs = FileSystemStorage()
import datetime

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


class User(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    
    username = models.CharField(max_length=250, unique=True)
    password = models.CharField(max_length=250)
    email = models.EmailField(max_length=250, null=True)
    superuser = models.BooleanField(default=False)
    password_changed = models.BooleanField(default=False)
    description = models.TextField(null=True)
    photo = models.FileField(upload_to="files/uphoto/%Y/%m/%d", max_length=200, null=True, blank=True)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    settings = DictField(default={})

    def __repr__(self):
        return u"<User %s>" % (self.username)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_uniquely(self.name, self.__class__)
            #self.password = encrypt_password(self.password)
        else:
            self.modified_date = datetime.datetime.now()

        super(User, self).save(*args, **kwargs)

    def is_authenticated(self):
        return True

    def is_superuser(self):
        return self.superuser

    def is_client(self):
        return self.type == 'client'

    def is_developer(self):
        return self.type == 'developer'


class Message(models.Model):
    project = models.ForeignKey('Project', related_name='messages')
    milestone = models.ForeignKey('Milestone', related_name='messages', null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey('User', related_name='mymessages')
    content = models.TextField()


class MessageResponse(models.Model):
    parent = models.ForeignKey('Message', related_name='responses')
    owner = models.ForeignKey('User', related_name='myresponses')
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    file = models.FileField(upload_to="files/msgrsp/%Y/%m/%d", storage=fs, max_length=300, null=True, blank=True)


class MessageFile(models.Model):
    message = models.ForeignKey('Message', related_name="files")
    owner = models.ForeignKey("User", related_name="messagefiles")
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to="files/msg/%Y/%m/%d", storage=fs, max_length=300, null=True, blank=True)


PROJECT_TYPE_CHOICES = (
    ('standard', "Standard"),
    ('scrum', "Scrum"),
)

class Project(models.Model):
    name = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    type = models.CharField(max_length=50, choices=PROJECT_TYPE_CHOICES)
    desc = models.TextField(blank=False)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)

    owner = models.ForeignKey("User", related_name="projects")
    participants = models.ManyToManyField('User', related_name="projects_participant", through="ProjectUser", null=True, blank=True)
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


ROLE_CHOICES = (
    ('developer', 'Developer'),
    ('manager', 'Project manager'),
    ('partner', 'Partner'),
    ('client', 'Client'),
)


class ProjectUser(models.Model):
    project = models.ForeignKey("Project")
    user = models.ForeignKey("User")
    role = models.CharField(max_length=100, choices=ROLE_CHOICES)

    def __repr__(self):
        return u"<Project-User-Relation-%s>" % (self.id)

    class Meta:
        unique_together = ('project', 'user')


REPO_TYPES_CHOICES = (
    ('hg', 'Mercurial'),
)

class Repo(models.Model):
    type = models.CharField(max_length=50, choices=REPO_TYPES_CHOICES, default='hg')
    project = models.OneToOneField("Project", related_name="repo")
    relative_location = models.CharField(max_length=500, blank=True)

    def save(self, *args, **kwargs):
        if self.type == 'hg':
            if not self.id:
                full_path, relative_path = make_repo_location(self.project)
                self.relative_location = relative_path
                create_repository(full_path)

        if self.id:
            self.modified_date = datetime.datetime.now()

        super(Repo, self).save(*args, **kwargs)


    def delete(self, *args, **kwargs):
        if self.id and self.type == 'hg':
            full_path, relative_path = make_repo_location(self.project)
            delete_repository(full_path)

        super(Repo, self).delete(*args, **kwargs)



class Wiki(models.Model):
    """ Individual project wiki system. Realation table"""
    project = models.OneToOneField('Project', related_name="wiki", null=True)
    
    def __repr__(self):
        return u"<Wiki %s>" % (self.id)


class WikiPage(models.Model):
    wiki = models.ForeignKey('Wiki', related_name="pages")
    owner = models.ForeignKey('User', related_name="wikipages")
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    def __repr__(self):
        return u"<WikiPage %s>" % (self.slug)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_uniquely(self.name, self.__class__)
        else:
            self.modified_date = datetime.datetime.now()

        super(WikiPage, self).save(*args, **kwargs)


class WikiPageFile(models.Model):
    wikipage = models.ForeignKey("WikiPage", related_name="files")
    owner = models.ForeignKey('User', related_name="wikipagefiles")
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to="files/msg/%Y/%m/%d", storage=fs, max_length=300)


class WikiPageComment(models.Model):
    wikipage = models.ForeignKey("WikiPageComment", related_name="comments")
    owner = models.ForeignKey('User', related_name='wikicomments')
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to="wikicommentfiles/%Y/%m/%d", storage=fs, max_length=300, null=True, blank=True)
    content = models.TextField()


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


USER_STORY_POINTS_CHOICES = (
    (1.0, '1'),(2.0,'2'), (3.0, '3'), (4.0,'4'),
    (5.0, '5'),(8.0,'8'), (0.5, '1/2'),
)

class UserStory(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField()

    points = models.FloatField(choices=USER_STORY_POINTS_CHOICES)
    priority = models.IntegerField(default=50) 
    milestone = models.ForeignKey('Milestone', related_name='userstories')
    project = models.ForeignKey('Project', related_name='userstories')

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)

    closed = models.BooleanField(default=True)

    def __repr__(self):
        return u"<UserStory %s>" % (self.id)


    def save(self, *args, **kwargs):
        if self.id:
            self.modified_date = datetime.datetime.now()

        super(UserStory,self).save(*args, **kwargs)

    def percent_finished(self):
        from django.db.models import Q
        issues_opended = self.issues.filter(Q(status='new')|Q(status='accepted')).count()
        issues_closed = self.issues.filter(status='fixed').coount()
        return float(issues_closed * 100) / float(issues_opended + issues_closed)

    def is_finished(self):
        return self.percent_finished() == 100

    
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
    (0, 'Task'),
    (1, 'Bug'),
    (2, 'Enhancement'),
)

class Issue(models.Model):
    type = models.IntegerField(choices=ISSUE_TYPE_CHOICES)
    priority = models.IntegerField(choices=ISSUE_TYPE_CHOICES)
    status = models.CharField(max_length=50, choices=ISSUE_STATUS_CHOICES)
    milestone = models.ForeignKey("Milestone", related_name="issues")
    
    project = models.ForeignKey("Project", related_name="issues")
    us = models.ForeignKey("UserStory", related_name="issues", null=True, default=None)
    author = models.ForeignKey("User", null=True, default=None, related_name="issues")

    priority = models.IntegerField(choices=ISSUE_PRIORITY_CHOICES, default=2)
    watchers = models.ForeignKey("User", null=True, default=None)
    
    subj = models.CharField(max_length=250)
    desc = models.TextField()

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    finish_date = models.DateTimeField(null=True, blank=True)
    tested = models.BooleanField(default=False)


    def __repr__(self):
        return u"<Issue %s>" % (self.id)

    def save(self, *args, **kwargs):
        if self.id:
            self.modified_date = datetime.datetime.now()

        super(Issue,self).save(*args, **kwargs)


class IssueResponse(models.Model):
    """ Issue comments model. """
    issue = models.ForeignKey("Issue", related_name="responses")
    owner = models.ForeignKey("User", related_name="issueresponses")
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    file = models.FileField(upload_to="files/msgrsp/%Y/%m/%d", storage=fs, max_length=300, null=True, blank=True)


class IssueFile(models.Model):
    """ Issue attachments model. """
    issue = models.ForeignKey("Issue", related_name="attachments", null=True)
    owner = models.ForeignKey("User", related_name="issuefiles")
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to="files/msg/%Y/%m/%d", storage=fs, max_length=300, null=True, blank=True)
    desc = models.TextField(blank=True)


class File(models.Model):
    project = models.ForeignKey("Project", related_name="files")
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    desc = models.TextField()
    owner = models.ForeignKey("User", related_name="files")


class FileHistory(models.Model):
    file = models.ForeignKey("File", related_name="history")
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    desc = models.TextField()
    owner = models.ForeignKey("User", related_name="historyfiles")


class PostSecurity(models.Model):
    """ Sirve para controlar el ratio de posts y asi evitar spam massivo. """
    remote_host = models.CharField(max_length=200, unique=True)
    last_post = models.DateTimeField(auto_now_add=True)


class Blacklist(models.Model):
    """ Sirve para poner una lista negra de ips que directamente no pueden
    acceder al sitio. """
    remote_host = models.CharField(max_length=200, unique=True)

