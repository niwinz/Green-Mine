# -*- coding: utf-8 -*-

from django import forms
from greenmine.base.models import *
from greenmine.scrum.models import *

class TaskCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project')
        super(TaskCreateForm, self).__init__(*args, **kwargs)

        self.fields['assigned_to'].queryset = self.project\
            .all_participants.order_by('first_name', 'last_name')

        self.fields['user_story'].queryset = self.project\
            .user_stories.order_by('-created_date')
        self.fields['user_story'].required = True

    class Meta:
        model = models.Task
        fields = (
            'user_story',
            'priority',
            'subject',
            'description',
            'assigned_to',
        )

class TaskEditForm(TaskCreateForm):
    pass
