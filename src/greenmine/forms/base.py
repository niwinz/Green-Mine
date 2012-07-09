# -*- codins: utf-8 -*-

from django import forms
from django.conf import settings
from django.contrib import messages

from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import PasswordInput, TextInput
from django.forms.extras.widgets import SelectDateWidget
from django.forms.widgets import Textarea
from django.forms.fields import CharField as DjangoCharField

from greenmine.questions.models import *
from greenmine.wiki.widgets import WikiWidget
from greenmine.base.models import *
from greenmine.scrum.models import *

import json

class CharField(DjangoCharField):
    """ jQuery-validator friendly charfield """
    def __init__(self, *args, **kwargs):
        self._widget_type = kwargs.pop('type', 'text')
        super(CharField, self).__init__(*args, **kwargs)

    def widget_attrs(self, widget):
        attrs = super(CharField, self).widget_attrs(widget)
        if not attrs:
            attrs = {}

        if self.min_length:
            attrs.update({'minlength':self.min_length})

        if "class" not in attrs:
            attrs['class'] = ''

        current_clases = attrs['class'].split()
        if self.required:
            attrs['required'] = 'required'
            if "required" not in current_clases:
                current_clases.append('required')

        if self._widget_type:
            widget.input_type = self._widget_type

        attrs['class'] = ' '.join(current_clases)
        return attrs


class DocumentForm(forms.Form):
    title = forms.CharField(max_length=200)
    document = forms.FileField(required=True)

    def __init__(self, *args, **kwargs):
        super(DocumentForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['required'] = 'true'
        self.fields['document'].widget.attrs['required'] = 'true'


class LoginForm(forms.Form):
    username = forms.CharField(max_length=200, min_length=4, label=_(u'Username'))
    password = forms.CharField(max_length=200, min_length=4, label=_(u'Password'), widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self._request = kwargs.pop('request', None)
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = self.cleaned_data

        if "username" in cleaned_data and "password" in cleaned_data:
            from django.contrib.auth import authenticate, login
            self._user = authenticate(
                username = cleaned_data['username'],
                password = cleaned_data['password']
            )
            if not self._user:
                msg = _(u'Username not exists or incorrect password')
                self._errors["username"] = self.error_class([msg])
                del cleaned_data["username"]
                del cleaned_data["password"]
            elif not self._user.is_active:
                msg = _(u'Username is deactivated')
                self._errors["username"] = self.error_class([msg])
                del cleaned_data["username"]
                del cleaned_data["password"]
            else:
                login(self._request, self._user)

        return cleaned_data


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=200, min_length=4,
        required=True, label=_(u'Username'))
    first_name = forms.CharField(max_length=200,
        required=True, label=_(u"First name"))
    last_name = forms.CharField(max_length=200,
        required=True, label=_(u"Last name"))
    email = forms.EmailField(max_length=200,
        required=True, label=_(u"Email"))

    password = forms.CharField(max_length=200, widget=forms.PasswordInput,
        label=_(u'Enter your new password'))
    password2 = forms.CharField(max_length=200, widget=forms.PasswordInput,
        label=_(u'Retype the password'))

    def clean(self):
        cleaned_data = self.cleaned_data

        if "username" in cleaned_data:
            username = cleaned_data['username']
            try:
                self.user = User.objects.get(username=username)
                msg = _(u"The username is already taken.")
                self._errors['username'] = self.error_class([msg])
                del cleaned_data['username']
            except User.DoesNotExist:
                pass

        if 'password2' in cleaned_data and 'password' in cleaned_data:
            if cleaned_data['password'] != cleaned_data['password2']:
                self._errors['password2'] = self.error_class(
                    [_(u'Passwords do not match')]
                )
                del cleaned_data['password2']
                del cleaned_data['password']

        return cleaned_data


class ForgottenPasswordForm(forms.Form):
    email = CharField(max_length=200, min_length=4,
        required=True, type='text', label=_(u'E-Mail'))

    def clean(self):
        cleaned_data = self.cleaned_data
        if "email" in cleaned_data:
            try:
                self.user = User.objects.get(email=cleaned_data['email'])
            except User.DoesNotExist:
                self._errors['email'] = self.error_class(
                    [_(u'The email does not correspond to any registered user.')]
                )
                del cleaned_data['email']
                return cleaned_data

        return cleaned_data


class PasswordRecoveryForm(forms.Form):
    password = forms.CharField(max_length=200, widget=forms.PasswordInput,
        label=_(u'Enter your new password'))
    password2 = forms.CharField(max_length=200, widget=forms.PasswordInput,
        label=_(u'Retype the password'))

    def clean(self):
        cleaned_data = self.cleaned_data
        if 'password2' in cleaned_data and 'password' in cleaned_data:
            if cleaned_data['password'] != cleaned_data['password2']:
                self._errors['password2'] = self.error_class(
                    [_(u'Passwords do not match')]
                )
                del cleaned_data['password2']
                del cleaned_data['password']

        return cleaned_data


class ProfileForm(forms.ModelForm):
    description = forms.CharField(widget=Textarea, required=False,
        label=_(u'Description'))
    photo = forms.ImageField(required=False, label=_(u'Photo'))

    class Meta:
        model = User
        fields = ('first_name', 'last_name',
                  'email', 'description', 'photo')

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance:
            kwargs['initial'] = {
                'description': instance.get_profile().description,
            }
        super(ProfileForm, self).__init__(*args,**kwargs)

    def save(self, *args, **kwargs):
        instance = super(ProfileForm, self).save(*args, **kwargs)
        profile = self.instance.get_profile()
        profile.description = self.cleaned_data['description']

        if self.cleaned_data['photo']:
            profile.photo = self.cleaned_data['photo']

        profile.save()
        return instance


class UserEditForm(ProfileForm):
    """
    Administration form for create or edit user.
    """

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',
                  'email', 'description', 'photo',
                  'is_active', 'is_staff', 'is_superuser')


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
        fields = ('priority', 'points', 'category', 'subject', 'description',
                'finish_date', 'client_requirement', 'team_requirement')


class UserStoryFormInline(forms.ModelForm):
    class Meta:
        model = UserStory
        fields = ('priority', 'points', 'status', 'category',
            'tested', 'finish_date', 'milestone')


class CommentForm(forms.Form):
    description = forms.CharField(max_length=2000, widget=forms.Textarea, required=True)
    attached_file = forms.FileField(required=False)

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)


class TaskForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)

        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['user_story'].queryset = self.project.user_stories.order_by('subject')
        self.fields['assigned_to'].queryset = self.project\
            .all_participants.order_by('first_name', 'last_name')
        self.fields['milestone'].queryset = self.project.milestones.order_by('-created_date')

    class Meta:
        fields = ('status', 'priority', 'subject','milestone',
            'description', 'assigned_to','type', 'user_story')
        model = Task

    def clean(self):
        cleaned_data = self.cleaned_data

        if "milestone" not in cleaned_data and "user_story" not in cleaned_data:
            self._errors['milestone'] = self.error_class([_(u"You need select one milestone or user story")])
            self._errors['user_story'] = self.error_class([_(u"You need select one milestone or user story")])

        return cleaned_data
