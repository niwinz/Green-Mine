# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.utils import simplejson

from django.forms.widgets import PasswordInput, TextInput
from django.utils.translation import ugettext_lazy as _
from django.forms.extras.widgets import SelectDateWidget
from django.forms.widgets import Textarea
from django.forms.fields import CharField as DjangoCharField

from greenmine.models import *
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

    def clean(self):
        cleaned_data = self.cleaned_data

        if "username" in cleaned_data and "password" in cleaned_data:
            print cleaned_data
            try:
                user = User.objects.get(username=cleaned_data['username'])
                if not user.check_password(cleaned_data['password']):
                    raise User.DoesNotExist()
                else:
                    self._user = user

            except User.DoesNotExist:
                msg = _(u'Username not exists or incorrect password')
                self._errors["username"] = self.error_class([msg])
                del cleaned_data["username"]
                del cleaned_data["password"]

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
            'description': self.instance.description,
            'email': self.instance.email,
        }
        super(ProfileForm, self).__init__(*args, **kwargs)

    def save(self):
        self.instance.username = self.cleaned_data['username']
        self.instance.password = encrypt_password(self.cleaned_data['password'])
        self.instance.description = self.cleaned_data['description']
        self.instance.photo = self.cleaned_data['photo']
        self.instance.save()
        return self.instance


class ProjectForm(Form):
    projectname = CharField(max_length=200, min_length=4,
        required=True, type='text', label=_(u'Nombre de proyecto'))
    description = CharField(widget=Textarea(), label=_(u'Descripcion'))

    def __init__(self, *args, **kwargs):
        self._request = kwargs.pop('request', None)
        super(ProjectForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = self.cleaned_data
        if "projectname" in cleaned_data and Project.objects\
            .filter(name=cleaned_data['projectname']).count() > 0:

            msg = _(u'Nombre de proyecto ya esta ocupado.')
            self._errors['projectname'] = self.error_class([msg])
            del cleaned_data['projectname']

        return cleaned_data

    def save(self):
        self.project = Project.objects.create(
            name = self.cleaned_data['projectname'],
            description = self.cleaned_data['description'],
            owner = self._request.user,
        )
        return self.project

