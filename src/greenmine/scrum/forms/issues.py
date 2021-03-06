# -*- coding: utf-8 -*-

from django import forms
from greenmine.base.models import *
from greenmine.scrum.models import *
from greenmine.taggit.models import Tag

class IssueFilterForm(forms.Form):
    order_by = forms.CharField(max_length=20, required=False) # TODO: conver to choice field
    status = forms.ChoiceField(choices=TASK_STATUS_CHOICES, required=False)
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)
    project = forms.ModelChoiceField(queryset=Project.objects.all(), required=False)
    assigned_to = forms.ModelChoiceField(queryset=User.objects.none(), required=False)
    severity = forms.ChoiceField(choices=TASK_SEVERITY_CHOICES, required=False)
    priority = forms.ChoiceField(choices=TASK_PRIORITY_CHOICES, required=False)

    milestone = forms.ModelChoiceField(
        queryset = Milestone.objects.none(),
        empty_label = None,
        required = False
    )

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project')
        super(IssueFilterForm, self).__init__(*args, **kwargs)
        self.fields['milestone'].queryset = self.project.milestones.all()

        self.fields['assigned_to'].queryset = self.project\
            .all_participants.order_by('first_name', 'last_name')

class IssueCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project')
        super(IssueCreateForm, self).__init__(*args, **kwargs)

        self.fields['assigned_to'].queryset = self.project\
            .all_participants.order_by('first_name', 'last_name')

        self.fields['milestone'].queryset = self.project\
            .milestones.order_by('-created_date')

    class Meta:
        model = Task
        fields = (
            'milestone',
            'status',
            'priority',
            'subject',
            'description',
            'assigned_to',
            'tags',
        )
