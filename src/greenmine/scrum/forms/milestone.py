from django import forms
from greenmine.scrum.models import *

class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ('name', 'estimated_start', 'estimated_finish', 'disponibility')

    def __init__(self, *args, **kwargs):
        super(MilestoneForm, self).__init__(*args, **kwargs)
        self.fields['estimated_finish'].widget.attrs.update({'autocomplete':'off'})
        self.fields['estimated_start'].widget.attrs.update({'autocomplete':'off'})


class UserStoryForm(forms.ModelForm):
    class Meta:
        model = UserStory
        fields = ('priority', 'points', 'subject', 'description', 'tags',
                'finish_date', 'client_requirement', 'team_requirement')


class UserStoryFormInline(forms.ModelForm):
    class Meta:
        model = UserStory
        fields = ('priority', 'points', 'tags',
            'tested', 'finish_date', 'milestone')
