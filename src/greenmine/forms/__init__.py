
# -*- codins: utf-8 -*-
from django import forms
from django.conf import settings
from django.utils import simplejson
from django.contrib import messages

from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import PasswordInput, TextInput
from django.forms.extras.widgets import SelectDateWidget
from django.forms.widgets import Textarea
from django.forms.fields import CharField as DjangoCharField

from django.utils import simplejson

from greenmine.models import *
from greenmine import models
from greenmine.utils import encrypt_password


class Form(forms.Form):
    """ Custom form with some jquery validator friendly propertys. """
    @property
    def jquery_errors(self):
        errors_object = {}
        for key, value in self.errors.iteritems():
            if isinstance(value, (list,tuple)) and len(value) > 0:
                errors_object[key] = value[0]

        return errors_object


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


class LoginForm(Form):
    username = CharField(max_length=200, min_length=4, 
        required=True, type='text', label=_(u'Username'))
    password = CharField(max_length=200, min_length=4, 
        required=True, type='password', label=_(u'Password'))

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



class ForgottenPasswordForm(Form):
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


class PasswordRecoveryForm(Form):
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
        fields = ('username', 'first_name', 'last_name',
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
    reset_password = forms.BooleanField(required=False,
        label = _(u"Reset password and send password recovery mail."))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',
                  'email', 'description', 'photo', 'reset_password')


class ProjectForm(Form):
    projectname = CharField(max_length=200, min_length=4,
        required=True, type='text', label=_(u'Project name'))
    description = CharField(widget=Textarea(), label=_(u'Description'))

    def __init__(self, *args, **kwargs):
        self._request = kwargs.pop('request', None)
        self.project = kwargs.pop('instance', None)
        if self.project:
            kwargs['initial'] = {
                'projectname': self.project.name,
                'description': self.project.description,
            }
        super(ProjectForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = self.cleaned_data        
        if self.project is None:
            if "projectname" in cleaned_data and Project.objects\
                .filter(name=cleaned_data['projectname']).count() > 0:

                messages.error(self._request, _(u'Project name is already occupied.'))
                raise forms.ValidationError(u'Project name is already occupied.')

        return cleaned_data

    def save(self):
        if self.project:
            self.project.name = self.cleaned_data['projectname']
            self.project.description = self.cleaned_data['description']
            self.project.save()
        else:
            self.project = Project.objects.create(
                name = self.cleaned_data['projectname'],
                description = self.cleaned_data['description'],
                owner = self._request.user,
            )
        return self.project


from django.forms.forms import BoundField


class ProjectPersonalSettingsForm(forms.Form):
    colors_hidden = forms.CharField(max_length=5000, required=False,
        widget=forms.HiddenInput)

    # email notifications
    send_email_on_us_created = forms.BooleanField(required=False, initial=True)
    send_email_on_us_modified = forms.BooleanField(required=False, initial=True)
    send_email_on_us_assigned = forms.BooleanField(required=False, initial=True)
    send_email_on_task_created = forms.BooleanField(required=False, initial=True)
    send_email_on_task_modified = forms.BooleanField(required=False, initial=True)
    send_email_on_task_assigned = forms.BooleanField(required=False, initial=True)
    send_email_on_question_created = forms.BooleanField(required=False, initial=True)
    send_email_on_question_response_created = forms.BooleanField(required=False, initial=True)

    posible_email_settings = [
        'send_email_on_us_created',
        'send_email_on_us_modified',
        'send_email_on_us_assigned',
        'send_email_on_task_created',
        'send_email_on_task_modified',
        'send_email_on_task_assigned',
        'send_email_on_question_created',
        'send_email_on_question_response_created',
    ]

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        if self.instance:
            initial_data = {}
            
            for key in self.posible_email_settings:
                current_value = self.instance.meta_email_settings.get(key, None)
                if current_value is not None:
                    initial_data[key] = current_value

            kwargs['initial'] = initial_data
        super(ProjectPersonalSettingsForm, self).__init__(*args, **kwargs)

    def _validate_colors(self, data):
        return True

    @property
    def email_fields_iterator(self):
        for key in self.posible_email_settings:
            yield BoundField(self, self.fields[key], key)

    def clean(self):
        cleaned_data = self.cleaned_data
        
        self.colors_data = {}
        if 'colors_hidden' in cleaned_data and cleaned_data['colors_hidden'].strip():
            self.colors_data = simplejson.loads(cleaned_data['colors_hidden'])
            if not self._validate_colors(self.colors_data):
                self._errors['colors_hidden'] = self.error_class([_(u"Invalid data")])
                del cleaned_data['colors_hidden']

        self.emails_data = {}
        for key in self.posible_email_settings:
            clean_value = cleaned_data.get(key, None)
            if clean_value is not None:
                self.emails_data[key] = clean_value

        return cleaned_data


class MilestoneForm(forms.ModelForm):
    class Meta:
        model = models.Milestone
        fields = ['name', 'estimated_finish']


class UserStoryForm(forms.ModelForm):
    class Meta:
        model = models.UserStory
        fields = ('priority', 'points', 'status', 'category',
            'tested', 'subject', 'description', 'finish_date')


class UserStoryFormInline(forms.ModelForm):
    class Meta:
        model = models.UserStory
        fields = ('priority', 'points', 'status', 'category',
            'tested', 'finish_date')


class QuestionCreateForm(forms.ModelForm):
    class Meta:
        model = models.Question
        exclude = ('project', 'owner', 'slug',)


class QuestionResponseForm(forms.ModelForm):
    class Meta:
        model = models.QuestionResponse
        exclude = ('owner', 'question', 'modified_date',)


class CommentForm(Form):
    description = forms.CharField(max_length=2000, widget=forms.Textarea, required=True)
    attached_file = forms.FileField(required=False)
    
    def __init__(self, *args, **kwargs):
        self._task = kwargs.pop('task', None)
        self._request = kwargs.pop('request', None)
        super(CommentForm, self).__init__(*args, **kwargs)
    
    def save(self):
        self._instance = models.TaskResponse.objects.create(
            owner = self._request.user,
            task = self._task,
            content = self.cleaned_data['description'],
        )

        if self.cleaned_data['attached_file']:
            instance_file = models.TaskAttachedFile.objects.create(
                response = self._instance,
                owner = self._request.user,
                task = self._task,
                attached_file = self.cleaned_data['attached_file']
            )


class TaskForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        self.initial_milestone = kwargs.pop('initial_milestone', None)
        self.initial_us = kwargs.pop('initial_us', None)

        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['user_story'].queryset = self.project.user_stories.all()
        self.fields['assigned_to'].queryset = self.project.all_participants
        self.fields['milestone'].queryset = self.project.milestones.order_by('-created_date')

        if self.initial_milestone:
            self.fields['milestone'].initial = self.initial_milestone
        else:
            self.fields['milestone'].initial = self.project.default_milestone

        if self.initial_us:
            self.fields['user_story'].initial = self.initial_us

        self.fields['milestone'].empty_label = None

    class Meta:
        fields = ('status', 'priority', 'subject','milestone',
            'description', 'assigned_to','type', 'user_story')
        model = models.Task


class DumpUploadForm(forms.Form):
    dumpfile = forms.FileField(required=True, widget=forms.FileInput(attrs={'class':'required'}))
    overwrite = forms.BooleanField(initial=True, required=False)


class WikiPageEditForm(forms.ModelForm):
    class Meta:
        model = models.WikiPage
        fields = ('content',)
