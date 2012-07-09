from django import foms
from greenmine.scrum.models import *

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'description')

    def clean_name(self):
        name = self.cleaned_data['name']
        if self.instance is None:
            projectqs = Project.objects.filter(name=name)

            if projectqs.count() > 0:
                raise forms.ValidationError("Project name is already taken.")

        return name


class ProjectPersonalSettingsForm(forms.ModelForm):
    class Meta:
        model = ProjectUserRole
        #exclude = ('project', 'user', 'role')
        fields = ('mail_milestone_created', 'mail_task_created', 'mail_task_assigned',
            'mail_userstory_created',)


class ProjectGeneralSettingsForm(forms.Form):
    colors_hidden = forms.CharField(max_length=5000, required=False,
        widget=forms.HiddenInput)

    markup = forms.ChoiceField(required=True,  choices=MARKUP_TYPE)

    sprints = forms.IntegerField(required=False)
    show_burndown = forms.BooleanField(required=False)
    show_burnup = forms.BooleanField(required=False)
    show_sprint_burndown = forms.BooleanField(required=False)
    total_story_points = forms.FloatField(required=False)


    def _validate_colors(self, data):
        return True

    def clean(self):
        cleaned_data = self.cleaned_data

        self.colors_data = {}
        if 'colors_hidden' in cleaned_data and cleaned_data['colors_hidden'].strip():
            self.colors_data = json.loads(cleaned_data['colors_hidden'])
            if not self._validate_colors(self.colors_data):
                self._errors['colors_hidden'] = self.error_class([_(u"Invalid data")])
                del cleaned_data['colors_hidden']

        return cleaned_data
