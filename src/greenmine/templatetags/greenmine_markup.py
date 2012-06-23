# -*- coding: utf-8 -*-

from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.html import escape
from django.utils.encoding import smart_str, force_unicode
from django.utils.safestring import mark_safe
from django.contrib.markup.templatetags.markup import restructuredtext

register = template.Library()

from docutils.parsers.rst import directives
import markdown

from greenmine.core.utils.markup import CodeBlock
directives.register_directive('code-block', CodeBlock)

def rst_filter(value, project):
    return restructuredtext(value)


from .plugin_wikilinks import WikiLinkExtension, makeExtension

def markdown_filter(value, project):
    wikilinks_extension = makeExtension([
        ('base_url', '/'+project.slug+'/wiki/'),
        ('end_url', ''),
        ('html_class', '')
    ])

    res = markdown.markdown(
        value,
        extensions = [wikilinks_extension, 'codehilite'],
        #extension_configs = {'wikilinks': [
        #                            ('base_url', '/'+project.slug+'/wiki/'),
        #                            ('end_url', ''),
        #                            ('html_class', '') ]},
        safe_mode = True
    )
    res = mark_safe(res)
    return res


@register.filter(is_safe=True, name="markup")
def markup_filter(value, project):
    if project.markup == 'rst':
        return rst_filter(value, project)
    elif project.markup == 'md':
        return markdown_filter(value, project)
    return value
