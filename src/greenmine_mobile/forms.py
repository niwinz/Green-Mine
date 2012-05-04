# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from greenmine.forms import Form, CharField
from greenmine import models


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
            try:
                user = User.objects.get(username = cleaned_data['username'])
            except User.DoesNotExist:
                msg = _(u'Username does not exists')
                self._errors["username"] = self.error_class([msg])
                del cleaned_data["username"]
                del cleaned_data["password"]
                return cleaned_data

            self._user = authenticate(
                username = cleaned_data['username'], 
                password = cleaned_data['password']
            )

            if not self._user:
                msg = _(u'Incorrect password')
                self._errors["password"] = self.error_class([msg])
                del cleaned_data["password"]

            elif not self._user.is_active:
                msg = _(u'Username is deactivated')
                self._errors["username"] = self.error_class([msg])
                del cleaned_data["username"]
                del cleaned_data["password"]

            else:
                login(self._request, self._user)

        return cleaned_data

class UsCreateForm(Form):
    subject = forms.CharField(max_length=200)
    description = forms.CharField(max_length=1000, widget=forms.Textarea)
    type = forms.ChoiceField(choices=models.US_TYPE_CHOICES, initial='us')
    priority = forms.TypedChoiceField(choices=models.US_PRIORITY_CHOICES, request=False, initial=2, coerce=int)
    estimation = forms.TypedChoiceField(choices=models.POINTS_CHOICES, required=False, coerce=float)
    status = fors.ChoiceField(choices=models.US_STATUS_CHOICES, required=False initial='open')
