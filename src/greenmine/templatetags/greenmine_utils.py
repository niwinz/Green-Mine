# -*- coding: utf-8 -*-

from django import template
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.encoding import smart_str, force_unicode
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name="hsize")
def human_size(value):
    if value / 1024.0**2 < 1:
        response = u"%.1f KB" % (value/1024.0)
    else:
        response = u"%.1f MB" % (value/1024.0**2)

    return mark_safe(response)


from greenmine.utils import normalize_tagname

@register.assignment_tag(takes_context=True)
def tag_color(context, tag):
    project = context['project']
    project_category_colors = project.meta_category_color

    ntagname = normalize_tagname(tag)
    if ntagname in project_category_colors:
        return project_category_colors[ntagname]

    return 'black'
