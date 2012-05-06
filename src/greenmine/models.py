# -* coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.files.storage import FileSystemStorage
from django.template.defaultfilters import slugify
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.contrib.auth.models import UserManager

from greenmine.fields import DictField, ListField

from django.utils import timezone
import datetime

ORG_ROLE_CHOICES = (
    ('owner', _(u'Owner')),
    ('developer', _(u'Developer')),
)

MARKUP_TYPE = (
    ('md', _(u'Markdown')),
    ('rst', _('Restructured Text')),
)

US_STATUS_CHOICES = (
    ('open', _(u'Open/New')),
    ('progress', _(u'In progress')),
    ('completed', _(u'Completed')),
    ('closed', _(u'Closed')),
)

TASK_PRIORITY_CHOICES = (
    (1, _(u'Low')),
    (3, _(u'Normal')),
    (5, _(u'High')),
)


TASK_TYPE_CHOICES = (
    ('bug', _(u'Bug')),
    ('task', _(u'Task')),
)

TASK_STATUS_CHOICES = US_STATUS_CHOICES

POINTS_CHOICES = (
    (-1, u'?'),
    (0, u'0'),
    (-2, u'1/2'),
    (1, u'1'),
    (2, u'2'),
    (3, u'3'),
    (5, u'5'),
    (8, u'8'),
    (10, u'10'),
)

TASK_COMMENT = 1
TASK_STATUS_CHANGE = 2
TASK_PRIORITY_CHANGE = 3
TASK_ASSIGNATION_CHANGE = 4

TASK_CHANGE_CHOICES = (
    (TASK_COMMENT, _(u"Task comment")),
    (TASK_STATUS_CHANGE, _(u"Task status change")),
    (TASK_PRIORITY_CHANGE, _(u"Task prioriy change")),
    (TASK_ASSIGNATION_CHANGE, _(u"Task assignation change")),
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


def ref_uniquely(project, model, field='ref'):
    """
    Returns a unique reference code based on base64 and time.
    """

    import time
    import baseconv

    # this prevents concurrent and inconsistent references.
    time.sleep(0.1)
    
    new_timestamp = lambda: int("".join(str(time.time()).split(".")))
    while True:
        potential = baseconv.base62.encode(new_timestamp())
        params = {field: potential, 'project': project}
        if not model.objects.filter(**params).exists():
            return potential

        time.sleep(0.0002)


class Profile(models.Model):
    user = models.OneToOneField("auth.User", related_name='profile')
    description = models.TextField(blank=True)
    photo = models.FileField(upload_to="files/msg",
        max_length=500, null=True, blank=True)

    default_language = models.CharField(max_length=20,
        null=True, blank=True, default=None)
    default_timezone = models.CharField(max_length=20,
        null=True, blank=True, default=None)
    token = models.CharField(max_length=200, unique=True,
        null=True, blank=True, default=None)


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


class ProjectManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)

    def can_view(self, user):
        queryset = ProjectUserRole.objects.filter(user=user)\
            .values_list('project', flat=True)
        return Project.objects.filter(pk__in=queryset)


class Project(models.Model):
    name = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField(blank=False)
    
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)

    owner = models.ForeignKey("auth.User", related_name="projects")
    participants = models.ManyToManyField('auth.User',
        related_name="projects_participant", through="ProjectUserRole",
        null=True, blank=True)

    public = models.BooleanField(default=True)

    fixed_story_points = models.IntegerField(default=0, null=True)
    meta_category_list = ListField(null=True, default=[], editable=False)
    meta_category_color = DictField(null=True, default={}, editable=False)
    markup = models.CharField(max_length=10, choices=MARKUP_TYPE, default='md')

    objects = ProjectManager()

    def natural_key(self):
        return (self.slug,)

    @property
    def unasociated_user_stories(self):
        return self.user_stories.filter(milestone__isnull=True)

    @property
    def all_participants(self):
        qs = ProjectUserRole.objects.filter(project=self)
        return User.objects.filter(id__in=qs.values_list('user__pk', flat=True))

    @property
    def default_milestone(self):
        return self.milestones.order_by('-created_date')[0]

    def __repr__(self):
        return u"<Project %s>" % (self.slug)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_uniquely(self.name, self.__class__)
        else:
            self.modified_date = timezone.now()

        super(Project, self).save(*args, **kwargs)

    def add_user(self, user, role):
        from greenmine import permissions
        return ProjectUserRole.objects.create(
            project = self,
            user = user,
            role = permissions.get_role(role),
        )
        

    """ Permalinks """

    @models.permalink
    def get_dashboard_url(self):
        return ('web:dashboard', (), {'pslug': self.slug})

    @models.permalink
    def get_backlog_url(self):
        return ('web:project-backlog', (),
            {'pslug': self.slug})

    @models.permalink
    def get_milestone_create_url(self):
        return ('web:milestone-create', (),
            {'pslug': self.slug})

    @models.permalink
    def get_userstory_create_url(self):
        return ('web:user-story-create', (), {'pslug': self.slug})

    @models.permalink
    def get_delete_api_url(self):
        return ('api:project-delete', (), {'pslug': self.slug})

    @models.permalink
    def get_edit_url(self):
        return ('web:project-edit', (), {'pslug': self.slug})        

    @models.permalink
    def get_export_url(self):
        return ('web:project-export-settings', (), {'pslug': self.slug})

    @models.permalink
    def get_export_now_url(self):
        return ('web:project-export-settings-now', (), {'pslug': self.slug})

    @models.permalink
    def get_export_rehash_url(self):
        return ('web:project-export-settings-rehash', (), {'pslug': self.slug})
        
    @models.permalink
    def get_default_tasks_url(self):
        return ('web:tasks-view', (), 
            {'pslug': self.slug, 'mid': self.default_milestone.id })

    @models.permalink
    def get_tasks_url(self):
        return ('web:tasks-view', (), {'pslug': self.slug})
    
    @models.permalink
    def get_settings_url(self):
        return ('web:project-personal-settings', (), {'pslug': self.slug})

    @models.permalink
    def get_general_settings_url(self):
        return ('web:project-general-settings', (), {'pslug': self.slug})

    @models.permalink
    def get_questions_url(self):
        return ('web:questions', (), {'pslug': self.slug})

    @models.permalink
    def get_questions_create_url(self):
        return ('web:questions-create', (), {'pslug': self.slug})


class Team(models.Model):
    name = models.CharField(max_length=200)
    project = models.ForeignKey('Project', related_name='teams')
    users = models.ManyToManyField('auth.User',
        related_name='teams', null=True, default=None)

    class Meta:
        unique_together = ('name', 'project')


class ProjectUserRole(models.Model):
    project = models.ForeignKey("Project", related_name="user_roles")
    user = models.ForeignKey("auth.User", related_name="user_roles")
    role = models.ForeignKey("Role", related_name="user_roles")

    # email notification settings
    meta_email_settings = DictField(null=True, default={}, editable=False)

    def __repr__(self):
        return u"<Project-User-Relation-%s>" % (self.id)

    class Meta:
        unique_together = ('project', 'user')


class MilestoneManager(models.Manager):
    def get_by_natural_key(self, name, project):
        return self.get(name=name, project__slug=project)


class Milestone(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    owner = models.ForeignKey('auth.User', related_name="milestones")
    project = models.ForeignKey('Project', related_name="milestones")
    estimated_finish = models.DateField(null=True, default=None)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    closed = models.BooleanField(default=False)

    meta_velocity = DictField(null=True, default={}, editable=False)
    objects = MilestoneManager()

    class Meta:
        ordering = ['-created_date']
        unique_together = ('name', 'project')

    @models.permalink
    def get_delete_url(self):
        return ('web:milestone-delete', (),
            {'pslug': self.project.slug, 'mid': self.id})

    @models.permalink
    def get_dashboard_url(self):
        return ('web:dashboard', (),
            {'pslug': self.project.slug, 'mid': self.id})

    @models.permalink
    def get_user_story_create_url(self):
        return ('web:user-story-create', (),
            {'pslug': self.project.slug, 'mid': self.id})

    @models.permalink
    def get_ml_detail_url(self):
        return ('web:milestone-dashboard', (),
            {'pslug': self.project.slug, 'mid': self.id})

    @models.permalink
    def get_create_task_url(self):
        return ('api:task-create', (),
            {'pslug': self.project.slug, 'mid': self.id})

    @models.permalink
    def get_stats_api_url(self):
        return ('api:stats-milestone', (),
            {'pslug': self.project.slug, 'mid': self.id})

    @models.permalink
    def get_tasks_url(self):
        return ('web:tasks-view', (), 
            {'pslug': self.project.slug, 'mid': self.id})

    @models.permalink
    def get_tasks_url_filter_by_task(self):
        return ('web:tasks-view', (), 
            {'pslug': self.project.slug, 'mid': self.id, 'filter_by':'task'})

    @models.permalink
    def get_tasks_url_filter_by_bug(self):
        return ('web:tasks-view', (), 
            {'pslug': self.project.slug, 'mid': self.id, 'filter_by':'bug'})

    @models.permalink
    def get_task_create_url(self):
        return ('web:task-create', (), 
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
            self.modified_date = timezone.now()

        super(Milestone, self).save(*args, **kwargs)


class UserStory(models.Model):
    ref = models.CharField(max_length=200, unique=True,
        db_index=True, null=True, default=None)
    milestone = models.ForeignKey("Milestone", blank=True,
        related_name="user_stories", null=True, default=None)
    project = models.ForeignKey("Project", related_name="user_stories")
    owner = models.ForeignKey("auth.User", null=True,
        default=None, related_name="user_stories")
    priority = models.IntegerField(default=1)
    points = models.IntegerField(choices=POINTS_CHOICES, default=-1)
    status = models.CharField(max_length=50,
        choices=US_STATUS_CHOICES, db_index=True, default="open")

    category = models.CharField(max_length=200, null=True, blank=True)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    tested = models.BooleanField(default=False)

    subject = models.CharField(max_length=500)
    description = models.TextField()
    finish_date = models.DateTimeField(null=True, blank=True)

    watchers = models.ManyToManyField('auth.User',
        related_name='us_watch', null=True)

    client_requirement = models.BooleanField(default=False)

    class Meta:
        unique_together = ('ref', 'project')

    def __repr__(self):
        return u"<UserStory %s>" % (self.id)

    def __unicode__(self):
        return self.ref + " - " + self.subject

    def save(self, *args, **kwargs):
        if self.id:
            self.modified_date = timezone.now()
        if not self.ref:
            self.ref = ref_uniquely(self.project, self.__class__)

        super(UserStory, self).save(*args, **kwargs)
    
    @models.permalink
    def get_assign_url(self):
        return ('web:assign-us', (),
            {'pslug': self.project.slug, 'iref': self.ref})

    @models.permalink
    def get_unassign_url(self):
        return ('web:unassign-us', (),
            {'pslug': self.project.slug, 'iref': self.ref})

    @models.permalink
    def get_drop_api_url(self):
        # TODO: check if this url is used.
        return ('api:user-story-drop', (),
            {'pslug': self.project.slug, 'iref': self.ref})

    @models.permalink
    def get_view_url(self):
        return ('web:user-story', (),
            {'pslug': self.project.slug, 'iref': self.ref})

    @models.permalink
    def get_edit_url(self):
        return ('web:user-story-edit', (),
            {'pslug': self.project.slug, 'iref': self.ref})
            
    @models.permalink
    def get_edit_inline_url(self):
        return ('web:user-story-edit-inline', (),
            {'pslug': self.project.slug, 'iref': self.ref})            

    @models.permalink
    def get_delete_url(self):
        return ('web:user-story-delete', (),
            {'pslug': self.project.slug, 'iref': self.ref})

    @models.permalink
    def get_task_create_url(self):
        return ('web:task-create', (),
            {'pslug': self.project.slug, 'iref': self.ref})

    """ Propertys """

    @property
    def tasks_new(self):
        return self.tasks.filter(status='open')

    @property
    def tasks_progress(self):
        return self.tasks.filter(status='progress')

    @property
    def tasks_closed(self):
        return self.tasks.filter(status__in=['closed', 'completed'])


class Change(models.Model):
    change_type = models.IntegerField(choices=TASK_CHANGE_CHOICES)
    owner = models.ForeignKey('auth.User', related_name='changes')
    created_date = models.DateTimeField(auto_now_add=True)

    project = models.ForeignKey("Project", related_name="changes")
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    data = DictField()


class ChangeAttachment(models.Model):
    change = models.ForeignKey("Change", related_name="attachments")
    owner = models.ForeignKey("auth.User", related_name="change_attachments")

    created_date = models.DateTimeField(auto_now_add=True)
    attached_file = models.FileField(upload_to="files/msg",
        max_length=500, null=True, blank=True)


class Task(models.Model):
    user_story = models.ForeignKey('UserStory', related_name='tasks', null=True, blank=True)
    ref = models.CharField(max_length=200, unique=True,
        db_index=True, null=True, default=None)
    status = models.CharField(max_length=50,
        choices=TASK_STATUS_CHOICES, default='open')
    owner = models.ForeignKey("auth.User", null=True,
        default=None, related_name="tasks")

    priority = models.IntegerField(choices=TASK_PRIORITY_CHOICES, default=3)
    milestone = models.ForeignKey('Milestone', related_name='tasks',
        null=True, default=None, blank=True)

    project = models.ForeignKey('Project', related_name='tasks')
    type = models.CharField(max_length=10,
        choices=TASK_TYPE_CHOICES, default='task')

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)

    subject = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey('auth.User',
        related_name='user_storys_assigned_to_me',
        blank=True, null=True, default=None)

    watchers = models.ManyToManyField('auth.User',
        related_name='task_watch', null=True)

    changes = generic.GenericRelation(Change)

    class Meta:
        unique_together = ('ref', 'project')

    @models.permalink
    def get_edit_url(self):
        return ('web:task-edit', (), {
            'pslug': self.project.slug,
            'tref': self.ref
        })

    @models.permalink
    def get_alter_api_url(self):
        return ('api:task-alter', (), {
            'pslug': self.project.slug,
            'taskref': self.ref
        })

    @models.permalink
    def get_reassign_api_url(self):
        return ('api:task-reassing', (), {
            'pslug': self.project.slug,
            'taskref': self.ref
        })

    @models.permalink
    def get_view_url(self):
        return ('web:task-view', (), 
            {'pslug':self.project.slug, 'tref': self.ref})

    @models.permalink
    def get_delete_url(self):
        return ('web:task-delete', (),
            {'pslug':self.project.slug, 'tref': self.ref})

    def save(self, *args, **kwargs):
        if self.id:
            self.modified_date = timezone.now()
            
        if not self.ref:
            self.ref = ref_uniquely(self.project, self.__class__)

        super(Task, self).save(*args, **kwargs)


class Question(models.Model):
    subject = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, max_length=250, blank=True)
    content = models.TextField()
    closed = models.BooleanField(default=False)
    attached_file = models.FileField(upload_to="messages",
        max_length=500, null=True, blank=True)

    project = models.ForeignKey('Project', related_name='questions')
    milestone = models.ForeignKey('Milestone', related_name='questions',
        null=True, default=None, blank=True)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey('auth.User', related_name='questions')

    watchers = models.ManyToManyField('auth.User',
        related_name='question_watch', null=True)

    @models.permalink
    def get_view_url(self):
        return ('web:questions-view', (), 
            {'pslug': self.project.slug, 'qslug': self.slug})

    @models.permalink
    def get_edit_url(self):
        return ('web:questions-edit', (),
            {'pslug': self.project.slug, 'qslug': self.slug})

    @models.permalink
    def get_delete_url(self):
        return ('web:questions-delete', (),
            {'pslug': self.project.slug, 'qslug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_uniquely(self.subject, self.__class__)
        super(Question, self).save(*args, **kwargs)


class QuestionResponse(models.Model):
    content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    attached_file = models.FileField(upload_to="messages",
        max_length=500, null=True, blank=True)

    question = models.ForeignKey('Question', related_name='responses')
    owner = models.ForeignKey('auth.User', related_name='questions_responses')


class WikiPage(models.Model):
    project = models.ForeignKey('Project', related_name='wiki_pages')
    slug = models.SlugField(max_length=500, db_index=True)
    content = models.TextField(blank=False, null=True)

    watchers = models.ManyToManyField('auth.User',
        related_name='wikipage_watchers', null=True)

    @models.permalink
    def get_view_url(self):
        return ('web:wiki-page', (), 
            {'pslug': self.project.slug, 'wslug': self.slug})

    @models.permalink
    def get_edit_url(self):
        return ('web:wiki-page-edit', (),
            {'pslug': self.project.slug, 'wslug': self.slug})


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
