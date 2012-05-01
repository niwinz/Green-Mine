# -*- coding: utf-8 -*-

from django import template
from django.conf import settings
from django.utils.encoding import smart_str, force_unicode
from django.utils.safestring import mark_safe
from django.utils.html import escape

register = template.Library()

import markdown

from django.core.urlresolvers import reverse

@register.filter(name="markdown")
def markdown_filter(value, project):
    res = markdown.markdown(
        value,
        extensions = ['wikilinks', 'codehilite'], 
        extension_configs = {'wikilinks': [
                                    ('base_url', '/'+project+'/wiki/'), 
                                    ('end_url', ''),
                                    ('html_class', '') ]},
        safe_mode = True
    )
    res = mark_safe(res)
    return res


from django.contrib.markup.templatetags.markup import restructuredtext
from docutils.parsers.rst import directives
from greenmine.utils.markup import CodeBlock

directives.register_directive('code-block', CodeBlock)

@register.filter(is_safe=True, name="rst")
def rst_filter(valie, project):
    pass
    
    
    
