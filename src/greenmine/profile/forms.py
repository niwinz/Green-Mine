# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User

from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import PasswordInput, TextInput
from django.forms.extras.widgets import SelectDateWidget
from django.forms.widgets import Textarea

from greenmine.wiki.widgets import WikiWidget
#from greenmine.questions.models import *
#from greenmine.base.models import *
#from greenmine.scrum.models import *

import json


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
    email = forms.CharField(max_length=200, min_length=4,
        required=True, label=_(u'E-Mail'))

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
    tolorize_tags = forms.BooleanField(required=False, label=_(u'Set color for tags'))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username',
                  'email', 'description', 'photo', 'colorize_tags')

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance:
            kwargs['initial'] = {
                'description': instance.get_profile().description,
                'colorize_tags': instance.get_profile().colorize_tags,
            }
        super(ProfileForm, self).__init__(*args,**kwargs)

    def save(self, *args, **kwargs):
        instance = super(ProfileForm, self).save(*args, **kwargs)
        profile = self.instance.get_profile()
        profile.description = self.cleaned_data['description']
        profile.colorize_tags = self.cleaned_data['colorize_tags']

        if self.cleaned_data['photo']:
            profile.photo = self.cleaned_data['photo']

        profile.save()
        return instance

