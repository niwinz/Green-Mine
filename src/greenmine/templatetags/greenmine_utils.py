# -*- coding: utf-8 -*-

from django import template
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.encoding import smart_str, force_unicode
from django.utils.safestring import mark_safe


from greenmine.core.utils import normalize_tagname

register = template.Library()

@register.filter(name="hsize")
def human_size(value):
    if value / 1024.0**2 < 1:
        response = u"%.1f KB" % (value/1024.0)
    else:
        response = u"%.1f MB" % (value/1024.0**2)

    return mark_safe(response)



@register.assignment_tag(takes_context=True)
def tag_color(context, tag):
    project = context['project']
    project_category_colors = project.meta_category_color

    ntagname = normalize_tagname(tag)
    if ntagname in project_category_colors:
        return project_category_colors[ntagname]

    return 'black'

@register.simple_tag(takes_context=True)
def dashboard_task(context, task):
    template_context = {
        'task': task,
        'participants': context['participants'],
        'status_list': context['status_list'],
        'project': context['project'],
    }
    return render_to_string("dashboard-userstory-task.html", template_context)


from superview.utils import LazyEncoder
import json

@register.assignment_tag(name="to_json")
def to_json_tag(tasks):
    if not isinstance(tasks, (list, tuple)):
        tasks = tuple(tasks)
    json_data = json.dumps(tasks, cls=LazyEncoder, sort_keys=False)
    return mark_safe(json_data)
