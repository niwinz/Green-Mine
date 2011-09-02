# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.utils import simplejson
from django.contrib import messages

from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import PasswordInput, TextInput
from django.forms.extras.widgets import SelectDateWidget
from django.forms.widgets import Textarea
from django.forms.fields import CharField as DjangoCharField

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
            if "required" not in current_clases:
                current_clases.append('required')
        
        if self._widget_type:
            widget.input_type = self._widget_type

        attrs['class'] = ' '.join(current_clases)
        return attrs


class LoginForm(Form):
    username = CharField(max_length=200, min_length=4, 
        required=True, type='text', label=_(u'Nombre de usuario'))
    password = CharField(max_length=200, min_length=4, 
        required=True, type='password', label=_(u'Contraseña'))

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


class ProfileForm(Form):
    username = CharField(max_length=200, min_length=4, 
        required=True, type='text', label=_(u'Nombre de usuario'))
    password = CharField(max_length=200, min_length=4, 
        required=False, type='password', label=_(u'Contraseña'))
    email = CharField(max_length=200, min_length=4, 
        required=True, type='text', label=_(u'E-Mail'))
    description = forms.CharField(widget=Textarea, required=False,
        label=_(u'Descripcion'))
    photo = forms.ImageField(required=False, label=_(u'Foto'))

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance')
        kwargs['initial'] = {
            'username': self.instance.username,
            'password': '',
            'description': self.instance.get_profile().description,
            'email': self.instance.email,
        }
        super(ProfileForm, self).__init__(*args, **kwargs)

    def save(self):
        self.instance.username = self.cleaned_data['username']
        self.instance.email = self.cleaned_data['email']
        profile = self.instance.get_profile()
        profile.description = self.cleaned_data['description']
        profile.photo = self.cleaned_data['photo']
        profile.save()
        self.instance.set_password(self.cleaned_data['password'])
        return self.instance



class ProjectForm(Form):
    projectname = CharField(max_length=200, min_length=4,
        required=True, type='text', label=_(u'Nombre de proyecto'))
    description = CharField(widget=Textarea(), label=_(u'Descripcion'))

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
        if "projectname" in cleaned_data and Project.objects\
            .filter(name=cleaned_data['projectname']).count() > 0:

            messages.error(self._request, _(u'Nombre de proyecto ya esta ocupado.'))
            raise forms.ValidationError(u'Nombre de proyecto ya esta ocupado.')

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


class FiltersForm(Form):
    priority = forms.ChoiceField(choices=(('', _(u'US priority...'),),) + US_PRIORITY_CHOICES)
    type = forms.ChoiceField(choices=(('', _(u'US type...'),),) + US_TYPE_CHOICES)

    def __init__(self, *args, **kwargs):
        queryset = kwargs.pop('queryset', None)
        super(FiltersForm, self).__init__(*args, **kwargs)


class MilestoneForm(Form):
    name = CharField(max_length=200, required=True)
    finish_date = forms.DateField(required=False, localize=True)

    def __init__(self, *args, **kwargs):
        self._instance = kwargs.pop('instance', None)
        if self._instance:
            kwargs['initial'] = {
                'name': self._instance.name,
                'finish_date': self._instance.estimated_finish,
            }
        super(MilestoneForm,self).__init__(*args, **kwargs)

    def save(self, commit=True):
        if not self._instance:
            self._instance = Milestone()

        self._instance.name = self.cleaned_data['name']
        self._instance.estimated_finish = self.cleaned_data['finish_date']
        if commit:
            self._instance.save()
        return self._instance


class UsForm(Form):
    #: TODO: refactor whis
    name = CharField(max_length=200, required=True)
    type = forms.ChoiceField(choices=US_TYPE_CHOICES)
    status = forms.ChoiceField(choices=US_STATUS_CHOICES)
    description = CharField(max_length=1000, required=False)
    milestone = forms.ModelChoiceField(queryset=Milestone.objects.none(), required=False)

    def __init__(self, *args, **kwargs):
        milestone_queryset = kwargs.pop('milestone_queryset', Milestone.objects.none())
        self._instance = kwargs.pop('instance', None)
        if self._instance:
            kwargs['initial'] = {
                'name': self._instance.subject,
                'type': self._instance.type,
                'status': self._instance.status,
                'description': self._instance.description,
                'milestone': self._instance.milestone,
            }

        super(UsForm, self).__init__(*args, **kwargs)
        self.fields['milestone'].queryset = milestone_queryset

    def save(self, commit=True):
        if not self._instance:
            self._instance = Us()

        self._instance.subject = self.cleaned_data['name']
        self._instance.type = self.cleaned_data['type']
        self._instance.status = self.cleaned_data['status']
        self._instance.description = self.cleaned_data['description']
        self._instance.milestone = self.cleaned_data['milestone']
        if commit:
            self._instance.save()
        return self._instance


class UsResponseForm(Form):
    description = forms.CharField(max_length=2000, widget=forms.Textarea, required=True)
    attached_file = forms.FileField(required=False)
    
    def __init__(self, *args, **kwargs):
        self._us = kwargs.pop('us', None)
        self._request = kwargs.pop('request', None)
        super(UsResponseForm, self).__init__(*args, **kwargs)

    def save(self):
        self._instance = models.UsResponse.objects.create(
            owner = self._request.user,
            us = self._us,
            content = self.cleaned_data['description'],
        )
        if self.cleaned_data['attached_file']:
            instance_file = models.UsFile.objects.create(
                response = self._instance,
                owner = self._request.user,
                attached_file = self.cleaned_data['attached_file']
            )


class DumpUploadForm(forms.Form):
    dumpfile = forms.FileField(required=True)
    overwrite = forms.BooleanField(initial=True, required=False)

