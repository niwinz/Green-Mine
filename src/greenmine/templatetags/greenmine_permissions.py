# -*- coding: utf-8 -*-

from django import template
from django.conf import settings
from django.utils.encoding import smart_str, force_unicode
from django.utils.safestring import mark_safe

register = template.Library()

from greenmine.models import ROLE_OBSERVER, ROLE_DEVELOPER, ROLE_MANAGER
from greenmine.models import ROLE_PARTNER, ROLE_CLIENT

from greenmine.utils.permission import check_role
from greenmine.utils.permission import has_project_role


@register.assignment_tag(takes_context=True)
def check_role_manager(context):
    project, user = context['project'], context['user']
    return check_role(project, ROLE_MANAGER, user)


@register.assignment_tag(takes_context=True)
def check_has_project_role(context):
    project, user = context['project'], context['user']
    return has_project_role(project, user)
