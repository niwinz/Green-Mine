# -*- coding: utf-8 -*-

from django import template
from django.conf import settings
from django.utils.encoding import smart_str, force_unicode
from django.utils.safestring import mark_safe

from greenmine.core import permissions

register = template.Library()

@register.assignment_tag(takes_context=True)
def check_role(context, loc, perms):
    project, user, perms = context['project'], context['user'], perms.split(",")
    return permissions.has_perms(user, project, (loc, perms))
