# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Milestone.estimated_start'
        db.add_column('greenmine_milestone', 'estimated_start',
                      self.gf('django.db.models.fields.DateField')(default=None, null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Milestone.estimated_start'
        db.delete_column('greenmine_milestone', 'estimated_start')


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
        'greenmine.document': {
            'Meta': {'object_name': 'Document'},
            'attached_file': ('django.db.models.fields.files.FileField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'documents'", 'to': "orm['auth.User']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'documents'", 'to': "orm['greenmine.Project']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '200', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'})
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
            'disponibility': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True'}),
            'estimated_finish': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True'}),
            'estimated_start': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            'extras': ('django.db.models.fields.related.OneToOneField', [], {'default': 'None', 'related_name': "'project'", 'unique': 'True', 'null': 'True', 'to': "orm['greenmine.ProjectExtras']"}),
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
        'greenmine.projectextras': {
            'Meta': {'object_name': 'ProjectExtras'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'show_burndown': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_burnup': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sprints': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'task_parser_re': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'total_story_points': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True'})
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
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
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
            'document_create': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'document_delete': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'document_edit': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'document_view': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
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
        'greenmine.temporalfile': {
            'Meta': {'object_name': 'TemporalFile'},
            'attached_file': ('django.db.models.fields.files.FileField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tmpfiles'", 'to': "orm['auth.User']"})
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
            'team_requirement': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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