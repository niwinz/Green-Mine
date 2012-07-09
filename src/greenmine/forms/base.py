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


from greenmine.profile.forms import ProfileForm

class UserEditForm(ProfileForm):
    """
    Administration form for create or edit user.
    """

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',
                  'email', 'description', 'photo',
                  'is_active', 'is_staff', 'is_superuser')


class CommentForm(forms.Form):
    description = forms.CharField(max_length=2000, widget=forms.Textarea, required=True)
    attached_file = forms.FileField(required=False)

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
