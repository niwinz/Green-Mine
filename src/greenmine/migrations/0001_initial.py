# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Profile'
        db.create_table('greenmine_profile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(related_name='profile', unique=True, to=orm['auth.User'])),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('photo', self.gf('django.db.models.fields.files.FileField')(max_length=500, null=True, blank=True)),
            ('default_language', self.gf('django.db.models.fields.CharField')(default=None, max_length=20, null=True, blank=True)),
            ('default_timezone', self.gf('django.db.models.fields.CharField')(default=None, max_length=20, null=True, blank=True)),
            ('token', self.gf('django.db.models.fields.CharField')(default=None, max_length=200, unique=True, null=True, blank=True)),
        ))
        db.send_create_signal('greenmine', ['Profile'])

        # Adding model 'Role'
        db.create_table('greenmine_role', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=250, blank=True)),
            ('project_view', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('project_edit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('project_delete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('userstory_view', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('userstory_create', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('userstory_edit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('userstory_delete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('milestone_view', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('milestone_create', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('milestone_edit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('milestone_delete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('task_view', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('task_create', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('task_edit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('task_delete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('wiki_view', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('wiki_create', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('wiki_edit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('wiki_delete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('question_view', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('question_create', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('question_edit', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('question_delete', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('greenmine', ['Role'])

        # Adding model 'Project'
        db.create_table('greenmine_project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=250)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=250, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='projects', to=orm['auth.User'])),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('fixed_story_points', self.gf('django.db.models.fields.IntegerField')(default=0, null=True)),
            ('meta_category_list', self.gf('django.db.models.fields.TextField')(default=[], null=True)),
            ('meta_category_color', self.gf('django.db.models.fields.TextField')(default={}, null=True)),
            ('markup', self.gf('django.db.models.fields.CharField')(default='md', max_length=10)),
        ))
        db.send_create_signal('greenmine', ['Project'])

        # Adding model 'Team'
        db.create_table('greenmine_team', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='teams', to=orm['greenmine.Project'])),
        ))
        db.send_create_signal('greenmine', ['Team'])

        # Adding unique constraint on 'Team', fields ['name', 'project']
        db.create_unique('greenmine_team', ['name', 'project_id'])

        # Adding M2M table for field users on 'Team'
        db.create_table('greenmine_team_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('team', models.ForeignKey(orm['greenmine.team'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('greenmine_team_users', ['team_id', 'user_id'])

        # Adding model 'ProjectUserRole'
        db.create_table('greenmine_projectuserrole', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='user_roles', to=orm['greenmine.Project'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='user_roles', to=orm['auth.User'])),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(related_name='user_roles', to=orm['greenmine.Role'])),
            ('meta_email_settings', self.gf('django.db.models.fields.TextField')(default={}, null=True)),
        ))
        db.send_create_signal('greenmine', ['ProjectUserRole'])

        # Adding unique constraint on 'ProjectUserRole', fields ['project', 'user']
        db.create_unique('greenmine_projectuserrole', ['project_id', 'user_id'])

        # Adding model 'Milestone'
        db.create_table('greenmine_milestone', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='milestones', to=orm['auth.User'])),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='milestones', to=orm['greenmine.Project'])),
            ('estimated_finish', self.gf('django.db.models.fields.DateField')(default=None, null=True)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('closed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('meta_velocity', self.gf('django.db.models.fields.TextField')(default={}, null=True)),
        ))
        db.send_create_signal('greenmine', ['Milestone'])

        # Adding unique constraint on 'Milestone', fields ['name', 'project']
        db.create_unique('greenmine_milestone', ['name', 'project_id'])

        # Adding model 'UserStory'
        db.create_table('greenmine_userstory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ref', self.gf('django.db.models.fields.CharField')(default=None, max_length=200, unique=True, null=True, db_index=True)),
            ('milestone', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='user_stories', null=True, blank=True, to=orm['greenmine.Milestone'])),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='user_stories', to=orm['greenmine.Project'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='user_stories', null=True, to=orm['auth.User'])),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('points', self.gf('django.db.models.fields.IntegerField')(default=-1)),
            ('status', self.gf('django.db.models.fields.CharField')(default='open', max_length=50, db_index=True)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('tested', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('finish_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('client_requirement', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('greenmine', ['UserStory'])

        # Adding unique constraint on 'UserStory', fields ['ref', 'project']
        db.create_unique('greenmine_userstory', ['ref', 'project_id'])

        # Adding M2M table for field watchers on 'UserStory'
        db.create_table('greenmine_userstory_watchers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userstory', models.ForeignKey(orm['greenmine.userstory'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('greenmine_userstory_watchers', ['userstory_id', 'user_id'])

        # Adding model 'Change'
        db.create_table('greenmine_change', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('change_type', self.gf('django.db.models.fields.IntegerField')()),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='changes', to=orm['auth.User'])),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='changes', to=orm['greenmine.Project'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('data', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('greenmine', ['Change'])

        # Adding model 'ChangeAttachment'
        db.create_table('greenmine_changeattachment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('change', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attachments', to=orm['greenmine.Change'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='change_attachments', to=orm['auth.User'])),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('attached_file', self.gf('django.db.models.fields.files.FileField')(max_length=500, null=True, blank=True)),
        ))
        db.send_create_signal('greenmine', ['ChangeAttachment'])

        # Adding model 'Task'
        db.create_table('greenmine_task', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_story', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='tasks', null=True, to=orm['greenmine.UserStory'])),
            ('ref', self.gf('django.db.models.fields.CharField')(default=None, max_length=200, unique=True, null=True, db_index=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='open', max_length=50)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='tasks', null=True, to=orm['auth.User'])),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=3)),
            ('milestone', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='tasks', null=True, blank=True, to=orm['greenmine.Milestone'])),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tasks', to=orm['greenmine.Project'])),
            ('type', self.gf('django.db.models.fields.CharField')(default='task', max_length=10)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('assigned_to', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='user_storys_assigned_to_me', null=True, blank=True, to=orm['auth.User'])),
        ))
        db.send_create_signal('greenmine', ['Task'])

        # Adding unique constraint on 'Task', fields ['ref', 'project']
        db.create_unique('greenmine_task', ['ref', 'project_id'])

        # Adding M2M table for field watchers on 'Task'
        db.create_table('greenmine_task_watchers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('task', models.ForeignKey(orm['greenmine.task'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('greenmine_task_watchers', ['task_id', 'user_id'])

        # Adding model 'Question'
        db.create_table('greenmine_question', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=250, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('closed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('attached_file', self.gf('django.db.models.fields.files.FileField')(max_length=500, null=True, blank=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='questions', to=orm['greenmine.Project'])),
            ('milestone', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='questions', null=True, blank=True, to=orm['greenmine.Milestone'])),
            ('assigned_to', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='questions', to=orm['auth.User'])),
        ))
        db.send_create_signal('greenmine', ['Question'])

        # Adding M2M table for field watchers on 'Question'
        db.create_table('greenmine_question_watchers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('question', models.ForeignKey(orm['greenmine.question'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('greenmine_question_watchers', ['question_id', 'user_id'])

        # Adding model 'QuestionResponse'
        db.create_table('greenmine_questionresponse', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('attached_file', self.gf('django.db.models.fields.files.FileField')(max_length=500, null=True, blank=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(related_name='responses', to=orm['greenmine.Question'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='questions_responses', to=orm['auth.User'])),
        ))
        db.send_create_signal('greenmine', ['QuestionResponse'])

        # Adding model 'WikiPage'
        db.create_table('greenmine_wikipage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='wiki_pages', to=orm['greenmine.Project'])),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=500)),
            ('content', self.gf('django.db.models.fields.TextField')(null=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='wiki_pages', null=True, to=orm['auth.User'])),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('greenmine', ['WikiPage'])

        # Adding M2M table for field watchers on 'WikiPage'
        db.create_table('greenmine_wikipage_watchers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('wikipage', models.ForeignKey(orm['greenmine.wikipage'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('greenmine_wikipage_watchers', ['wikipage_id', 'user_id'])

        # Adding model 'WikiPageHistory'
        db.create_table('greenmine_wikipagehistory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('wikipage', self.gf('django.db.models.fields.related.ForeignKey')(related_name='history_entries', to=orm['greenmine.WikiPage'])),
            ('content', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='wiki_page_historys', to=orm['auth.User'])),
        ))
        db.send_create_signal('greenmine', ['WikiPageHistory'])

        # Adding model 'WikiPageAttachment'
        db.create_table('greenmine_wikipageattachment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('wikipage', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attachments', to=orm['greenmine.WikiPage'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='wikifiles', to=orm['auth.User'])),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('attached_file', self.gf('django.db.models.fields.files.FileField')(max_length=500, null=True, blank=True)),
        ))
        db.send_create_signal('greenmine', ['WikiPageAttachment'])

        # Adding model 'ExportDirectoryCache'
        db.create_table('greenmine_exportdirectorycache', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('size', self.gf('django.db.models.fields.IntegerField')(null=True)),
        ))
        db.send_create_signal('greenmine', ['ExportDirectoryCache'])


    def backwards(self, orm):
        # Removing unique constraint on 'Task', fields ['ref', 'project']
        db.delete_unique('greenmine_task', ['ref', 'project_id'])

        # Removing unique constraint on 'UserStory', fields ['ref', 'project']
        db.delete_unique('greenmine_userstory', ['ref', 'project_id'])

        # Removing unique constraint on 'Milestone', fields ['name', 'project']
        db.delete_unique('greenmine_milestone', ['name', 'project_id'])

        # Removing unique constraint on 'ProjectUserRole', fields ['project', 'user']
        db.delete_unique('greenmine_projectuserrole', ['project_id', 'user_id'])

        # Removing unique constraint on 'Team', fields ['name', 'project']
        db.delete_unique('greenmine_team', ['name', 'project_id'])

        # Deleting model 'Profile'
        db.delete_table('greenmine_profile')

        # Deleting model 'Role'
        db.delete_table('greenmine_role')

        # Deleting model 'Project'
        db.delete_table('greenmine_project')

        # Deleting model 'Team'
        db.delete_table('greenmine_team')

        # Removing M2M table for field users on 'Team'
        db.delete_table('greenmine_team_users')

        # Deleting model 'ProjectUserRole'
        db.delete_table('greenmine_projectuserrole')

        # Deleting model 'Milestone'
        db.delete_table('greenmine_milestone')

        # Deleting model 'UserStory'
        db.delete_table('greenmine_userstory')

        # Removing M2M table for field watchers on 'UserStory'
        db.delete_table('greenmine_userstory_watchers')

        # Deleting model 'Change'
        db.delete_table('greenmine_change')

        # Deleting model 'ChangeAttachment'
        db.delete_table('greenmine_changeattachment')

        # Deleting model 'Task'
        db.delete_table('greenmine_task')

        # Removing M2M table for field watchers on 'Task'
        db.delete_table('greenmine_task_watchers')

        # Deleting model 'Question'
        db.delete_table('greenmine_question')

        # Removing M2M table for field watchers on 'Question'
        db.delete_table('greenmine_question_watchers')

        # Deleting model 'QuestionResponse'
        db.delete_table('greenmine_questionresponse')

        # Deleting model 'WikiPage'
        db.delete_table('greenmine_wikipage')

        # Removing M2M table for field watchers on 'WikiPage'
        db.delete_table('greenmine_wikipage_watchers')

        # Deleting model 'WikiPageHistory'
        db.delete_table('greenmine_wikipagehistory')

        # Deleting model 'WikiPageAttachment'
        db.delete_table('greenmine_wikipageattachment')

        # Deleting model 'ExportDirectoryCache'
        db.delete_table('greenmine_exportdirectorycache')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'greenmine.change': {
            'Meta': {'object_name': 'Change'},
            'change_type': ('django.db.models.fields.IntegerField', [], {}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'changes'", 'to': "orm['auth.User']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'changes'", 'to': "orm['greenmine.Project']"})
        },
        'greenmine.changeattachment': {
            'Meta': {'object_name': 'ChangeAttachment'},
            'attached_file': ('django.db.models.fields.files.FileField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'change': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachments'", 'to': "orm['greenmine.Change']"}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'change_attachments'", 'to': "orm['auth.User']"})
        },
        'greenmine.exportdirectorycache': {
            'Meta': {'object_name': 'ExportDirectoryCache'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'size': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        'greenmine.milestone': {
            'Meta': {'unique_together': "(('name', 'project'),)", 'object_name': 'Milestone'},
            'closed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'estimated_finish': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meta_velocity': ('django.db.models.fields.TextField', [], {'default': '{}', 'null': 'True'}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'milestones'", 'to': "orm['auth.User']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'milestones'", 'to': "orm['greenmine.Project']"})
        },
        'greenmine.profile': {
            'Meta': {'object_name': 'Profile'},
            'default_language': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'default_timezone': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'photo': ('django.db.models.fields.files.FileField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'profile'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'greenmine.project': {
            'Meta': {'object_name': 'Project'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'fixed_story_points': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'markup': ('django.db.models.fields.CharField', [], {'default': "'md'", 'max_length': '10'}),
            'meta_category_color': ('django.db.models.fields.TextField', [], {'default': '{}', 'null': 'True'}),
            'meta_category_list': ('django.db.models.fields.TextField', [], {'default': '[]', 'null': 'True'}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '250'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'projects'", 'to': "orm['auth.User']"}),
            'participants': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'projects_participant'", 'to': "orm['auth.User']", 'through': "orm['greenmine.ProjectUserRole']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '250', 'blank': 'True'})
        },
        'greenmine.projectuserrole': {
            'Meta': {'unique_together': "(('project', 'user'),)", 'object_name': 'ProjectUserRole'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meta_email_settings': ('django.db.models.fields.TextField', [], {'default': '{}', 'null': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_roles'", 'to': "orm['greenmine.Project']"}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_roles'", 'to': "orm['greenmine.Role']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_roles'", 'to': "orm['auth.User']"})
        },
        'greenmine.question': {
            'Meta': {'object_name': 'Question'},
            'assigned_to': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'attached_file': ('django.db.models.fields.files.FileField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'closed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'milestone': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'questions'", 'null': 'True', 'blank': 'True', 'to': "orm['greenmine.Milestone']"}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'questions'", 'to': "orm['auth.User']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'questions'", 'to': "orm['greenmine.Project']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '250', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'watchers': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'question_watch'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.User']"})
        },
        'greenmine.questionresponse': {
            'Meta': {'object_name': 'QuestionResponse'},
            'attached_file': ('django.db.models.fields.files.FileField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'questions_responses'", 'to': "orm['auth.User']"}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'responses'", 'to': "orm['greenmine.Question']"})
        },
        'greenmine.role': {
            'Meta': {'object_name': 'Role'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'milestone_create': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'milestone_delete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'milestone_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'milestone_view': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'project_delete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'project_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'project_view': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'question_create': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'question_delete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'question_edit': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'question_view': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '250', 'blank': 'True'}),
            'task_create': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'task_delete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'task_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'task_view': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'userstory_create': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'userstory_delete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'userstory_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'userstory_view': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'wiki_create': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'wiki_delete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'wiki_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'wiki_view': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'greenmine.task': {
            'Meta': {'unique_together': "(('ref', 'project'),)", 'object_name': 'Task'},
            'assigned_to': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'user_storys_assigned_to_me'", 'null': 'True', 'blank': 'True', 'to': "orm['auth.User']"}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'milestone': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'tasks'", 'null': 'True', 'blank': 'True', 'to': "orm['greenmine.Milestone']"}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'tasks'", 'null': 'True', 'to': "orm['auth.User']"}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tasks'", 'to': "orm['greenmine.Project']"}),
            'ref': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'unique': 'True', 'null': 'True', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'open'", 'max_length': '50'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'task'", 'max_length': '10'}),
            'user_story': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'tasks'", 'null': 'True', 'to': "orm['greenmine.UserStory']"}),
            'watchers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'task_watch'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'greenmine.team': {
            'Meta': {'unique_together': "(('name', 'project'),)", 'object_name': 'Team'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'teams'", 'to': "orm['greenmine.Project']"}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'default': 'None', 'related_name': "'teams'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.User']"})
        },
        'greenmine.userstory': {
            'Meta': {'unique_together': "(('ref', 'project'),)", 'object_name': 'UserStory'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'client_requirement': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'finish_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'milestone': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'user_stories'", 'null': 'True', 'blank': 'True', 'to': "orm['greenmine.Milestone']"}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'user_stories'", 'null': 'True', 'to': "orm['auth.User']"}),
            'points': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_stories'", 'to': "orm['greenmine.Project']"}),
            'ref': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'unique': 'True', 'null': 'True', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'open'", 'max_length': '50', 'db_index': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'tested': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'watchers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'us_watch'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'greenmine.wikipage': {
            'Meta': {'object_name': 'WikiPage'},
            'content': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'wiki_pages'", 'null': 'True', 'to': "orm['auth.User']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'wiki_pages'", 'to': "orm['greenmine.Project']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '500'}),
            'watchers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'wikipage_watchers'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'greenmine.wikipageattachment': {
            'Meta': {'object_name': 'WikiPageAttachment'},
            'attached_file': ('django.db.models.fields.files.FileField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'wikifiles'", 'to': "orm['auth.User']"}),
            'wikipage': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachments'", 'to': "orm['greenmine.WikiPage']"})
        },
        'greenmine.wikipagehistory': {
            'Meta': {'object_name': 'WikiPageHistory'},
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'wiki_page_historys'", 'to': "orm['auth.User']"}),
            'wikipage': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'history_entries'", 'to': "orm['greenmine.WikiPage']"})
        }
    }

    complete_apps = ['greenmine']