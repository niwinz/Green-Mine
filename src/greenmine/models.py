# -* coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.files.storage import FileSystemStorage
from django.template.defaultfilters import slugify
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User, UserManager

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

US_STATUS_CHOICES = (
    ('new', _(u'New')),
    ('accepted', _(u'In progress')),
    ('fixed', _(u'Fixed')),
    ('invalid', _(u'Invalid')),
    ('wontfix', _(u'Wontfix')),
    ('workaround', _(u'Workaround')),
    ('duplicate', _(u'Duplicated')),
)

US_PRIORITY_CHOICES = (
    (1, _(u'Lower')),
    (2, _(u'Normal')),
    (4, _(u'High')),
    (6, _(u'Urgent')),
    (8, _(u'Critical')),
)

US_TYPE_CHOICES = (
    ('us', _(u'User story')),
    ('bug', _(u'Bug')),
)

US_STATUS_CHOICES = (
    ('open', _(u'Open/New')),
    ('progess', _(u'In progress')),
    ('completed', _(u'Completed')),
    ('closed', _(u'Closed')),
)

POINTS_CHOICES = (
    (None, u'?'),
    (0.5, u'1/2'),
    (1, u'1'),
    (2, u'2'),
    (3, u'3'),
    (5, u'5')
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
    while True:
        potential = baseconv.base62.encode(int("".join(str(time.time()).split("."))))
        if not model.objects.filter(**{field: potential}).exists():
            return potential

        time.sleep(0.002)


class Profile(models.Model):
    user = models.ForeignKey("auth.User", unique=True)
    description = models.TextField(blank=True)
    photo = models.FileField(upload_to="files/msg/%Y/%m/%d", max_length=500, null=True, blank=True)
    default_language = models.CharField(max_length=20, null=True, blank=True, default=None)


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
        return ('web:project', (), {'pslug':self.slug})

    @models.permalink
    def get_unasigned_tasks_api_url(self):
        return ('api:us-for-poject', (), {'pslug':self.slug})

    @models.permalink
    def get_delete_api_url(self):
        return ('api:project-delete', (), {'pslug': self.slug})

    @models.permalink
    def get_milestone_create_api_url(self):
        return ('api:project-milestone-create', (), {'pslug': self.slug})

    @models.permalink
    def get_us_create_api_url(self):
        return ('api:project-us-create', (), {'pslug': self.slug})

    @models.permalink
    def get_milestones_list_api_url(self):
        return ('api:milestones-for-project', (), {'pslug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_uniquely(self.name, self.__class__)
        else:
            self.modified_date = datetime.datetime.now()

        super(Project, self).save(*args, **kwargs)


class Team(models.Model):
    name = models.CharField(max_length=200)
    project = models.ForeignKey('Project', related_name='teams')
    users = models.ManyToManyField('auth.User', related_name='teams', null=True, default=None)

    class Meta:
        unique_together = ('name', 'project')


class ProjectUserRole(models.Model):
    project = models.ForeignKey("Project")
    user = models.ForeignKey("auth.User")
    role = models.CharField(max_length=100, choices=ROLE_CHOICES)
    
    # email notification settings
    send_email_on_group_message = models.BooleanField(default=True)
    send_email_on_us_asignement = models.BooleanField(default=True)
    send_email_on_new_us = models.BooleanField(default=False)
    send_email_on_new_us_as_watcher = models.BooleanField(default=True)
    send_email_on_incoming_question = models.BooleanField(default=False)
    send_email_on_incoming_question_assigned = models.BooleanField(default=False)

    def __repr__(self):
        return u"<Project-User-Relation-%s>" % (self.id)

    class Meta:
        unique_together = ('project', 'user')


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
        return ('api:us-for-milestone', (), 
            {'pslug': self.project.slug, 'mid': self.id})

    @models.permalink
    def get_edit_api_url(self):
        return ('api:project-milestone-edit', (),
            {'pslug': self.project.slug, 'mid': self.id})

    class Meta(object):
        unique_together = ('name', 'project')

    def natural_key(self):
        return (self.name,) + self.project.natural_key()

    natural_key.dependencies = ['greenmine.Project']

    def __unicode__(self):
        return self.name
    
    def __repr__(self):
        return u"<Milestone %s>" % (self.id)

    def save(self, *args, **kwargs):
        if self.id:
            self.modified_date = datetime.datetime.now()

        super(Milestone, self).save(*args, **kwargs)


class Us(models.Model):
    ref = models.CharField(max_length=200, unique=True, db_index=True, null=True, default=None)
    milestone = models.ForeignKey("Milestone", related_name="uss", null=True, default=None)
    project = models.ForeignKey("Project", related_name="uss")
    type = models.CharField(max_length="50", default="us", choices=US_TYPE_CHOICES)
    owner = models.ForeignKey("auth.User", null=True, default=None, related_name="uss")
    priority = models.IntegerField(choices=US_PRIORITY_CHOICES, default=2)
    points = models.FloatField(choices=POINTS_CHOICES, null=True, default=None)
    status = models.CharField(max_length=50, choices=US_STATUS_CHOICES, db_index=True, default="open")

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    tested = models.BooleanField(default=False)
    
    subject = models.CharField(max_length=500)
    description = models.TextField()
    finish_date = models.DateTimeField(null=True, blank=True)

    def __repr__(self):
        return u"<Us %s>" % (self.id)

    def save(self, *args, **kwargs):
        if self.id:
            self.modified_date = datetime.datetime.now()
        if not self.ref:
            self.ref = ref_uniquely(self.__class__)

        super(Us,self).save(*args, **kwargs)

    @models.permalink
    def get_edit_api_url(self):
        return ('api:us-edit', (), {'pslug': self.project.slug, 'iref': self.ref})

    @models.permalink
    def get_asoiciate_api_url(self):
        return ('api:us-asociate', (), {'pslug': self.project.slug, 'iref': self.ref})

    @models.permalink
    def get_drop_api_url(self):
        return ('api:us-drop', (), {'pslug': self.project.slug, 'iref': self.ref})

    @models.permalink
    def get_view_url(self):
        return ('web:us', (), {'pslug': self.project.slug, 'iref': self.ref})


class Task(models.Model):
    us = models.ForeignKey('Us', related_name='tasks')
    ref = models.CharField(max_length=200, unique=True, db_index=True, null=True, default=None)
    status = models.CharField(max_length=50, choices=US_STATUS_CHOICES)
    owner = models.ForeignKey("auth.User", null=True, default=None, related_name="tasks")
    priority = models.IntegerField(choices=US_PRIORITY_CHOICES, default=2)
    
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    
    subject = models.CharField(max_length=500)
    description = models.TextField()
    assigned_to = models.ForeignKey('auth.User', related_name='uss_assigned_to_me', null=True, default=None)


class UsResponse(models.Model):
    us = models.ForeignKey('Us', related_name='responses')
    owner = models.ForeignKey('auth.User', related_name='responses')

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()


class UsFile(models.Model):
    response = models.ForeignKey('UsResponse', related_name='attached_files', null=True, blank=True)
    us = models.ForeignKey('Us', related_name='attached_files', null=True, blank=True)

    owner = models.ForeignKey("auth.User", related_name="files")
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    attached_file = models.FileField(upload_to="files/msg/%Y/%m/%d", max_length=500, null=True, blank=True)


class Question(models.Model):
    subject = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, max_length=200)
    content = models.TextField()
    closed = models.BooleanField(default=False)
    attached_file = models.FileField(upload_to="messages/%Y/%m/%d", max_length=500, null=True, blank=True)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey('auth.User', related_name='questions')


class QuestionResponse(models.Model):
    content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    attached_file = models.FileField(upload_to="messages/%Y/%m/%d", max_length=500, null=True, blank=True)

    question = models.ForeignKey('Question', related_name='responses')
    owner = models.ForeignKey('auth.User', related_name='questions_responses')


class GSettings(models.Model):
    key = models.CharField(max_length=200, unique=True)
    value = models.TextField(blank=True, default='')


# load signals
from . import sigdispatch
