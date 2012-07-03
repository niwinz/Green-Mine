# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django import forms
from .. import models

class ApiForm(forms.Form):
    status = forms.ChoiceField(choices=models.TASK_STATUS_CHOICES, required=False)
    us = forms.IntegerField(required=False)
    assignation = forms.IntegerField(required=False)
    task = forms.IntegerField(required=False)
