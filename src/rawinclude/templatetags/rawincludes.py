# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django import template
from django.core.exceptions import ImproperlyConfigured
from django.utils.safestring import mark_safe

register = template.Library()

from ..base import find_template

class RawIncludeNode(template.Node):
    def __init__(self, path):
        self.path = path

    def render(self, context):
        path = self.path.resolve(context)
        content = find_template(path)
        return mark_safe(content)


@register.tag(name="raw_include")
def raw_include(parser, token):
    try:
        tag_name, name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])

    return RawIncludeNode(parser.compile_filter(name))


#from django import template
#
#register = template.Library()
#
#def do_include_raw(parser, token):
#    """
#    Performs a template include without parsing the context, just dumps the template in.
#    """
#    bits = token.split_contents()
#    if len(bits) != 2:
#        raise TemplateSyntaxError, "%r tag takes one argument: the name of the template to be included" %
#bits[0]
#
#    template_name = bits[1]
#    if template_name[0] in ('"', "'") and template_name[-1] == template_name[0]:
#        template_name = template_name[1:-1]
#
#    source, path = load_template_source(template_name)
#
#    return template.TextNode(source)
#register.tag("include_raw", do_include_raw)
