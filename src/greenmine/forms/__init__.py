# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.utils import simplejson

from django.forms.widgets import PasswordInput, TextInput
from django.utils.translation import ugettext_lazy as _
from django.forms.extras.widgets import SelectDateWidget
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
    username = CharField(max_length=200, min_length=4, required=True, type='email')
    password = CharField(max_length=200, min_length=8, required=True, type='password')

    def clean(self):
        cleaned_data = self.cleaned_data

        if "username" in cleaned_data and "password" in cleaned_data:
            try:
                self._user = User.objects.get(username=form.cleaned_data['username'],
                    password=encrypt_password(form.cleaned_data['password']))

            except User.DoesNotExist:
                pass

        return cleaned_data
