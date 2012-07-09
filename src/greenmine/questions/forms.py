from django import forms
from greenmine.questions.models import *
from greenmine.base.models import *

class QuestionCreateForm(forms.ModelForm):
    class Meta:
        model = Question
        exclude = ('project', 'owner', 'slug')

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project')
        super(QuestionCreateForm, self).__init__(*args, **kwargs)

        participants = set([project.owner.pk])
        participants.update([x.pk for x in project.participants.only('pk').all()])

        self.fields['assigned_to'].queryset = User.objects.filter(pk__in=participants)


class QuestionResponseForm(forms.ModelForm):
    class Meta:
        model = QuestionResponse
        exclude = ('owner', 'question', 'modified_date',)

