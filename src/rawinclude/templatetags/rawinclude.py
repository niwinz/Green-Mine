# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django import template
from django.core.exceptions import ImproperlyConfigured
from django.utils.safestring import mark_safe

from ..base import find_template

register = template.Library()


class RawIncludeNode(template.Node):
    def __init__(self, path):
        self.path = path

    def render(self, context):
        path = self.path.resolve(context)
        source, path = find_template(path)
        return mark_safe(source)


@register.tag(name="raw_include")
def raw_include(parser, token):
    try:
        tag_name, name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])

    return RawIncludeNode(parser.compile_filter(name))
