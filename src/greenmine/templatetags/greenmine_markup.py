# -*- coding: utf-8 -*-

from django import template
from django.conf import settings
from django.utils.encoding import smart_str, force_unicode
from django.utils.safestring import mark_safe
from django.utils.html import escape

register = template.Library()

import markdown

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, TextLexer

import lxml.html as lx
import lxml.etree as et

from django.core.urlresolvers import reverse

class Postprocessor(markdown.postprocessors.Postprocessor):
    formatter = HtmlFormatter(noclasses=False, style="friendly")

    def run(self, lines):
        doc = lx.fromstring(lines)

        # Format and higlight code on pre blocks.
        for pre_elem in doc.cssselect('pre'):
            try:
                lexer = get_lexer_by_name(pre_elem.get('lang', '!'))
            except ValueError:
                lexer = TextLexer()
            
            escaped_text = pre_elem.text
            if escaped_text:
                new_text = highlight(escaped_text, lexer, self.formatter)

                pre_elem.clear()
                pre_elem.append(lx.fromstring(new_text))
                pre_elem.tag = 'div'

        return et.tostring(doc, pretty_print=False, method="html")


class PygmentsExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        post_processor = Postprocessor()
        md.postprocessors["pygments"] = post_processor
        md.registerExtension(self)


@register.filter(name="markdown")
def markdown_filter(value, project):
    res = markdown.markdown(
        value,
        extensions = ['wikilinks', PygmentsExtension()], 
        extension_configs = {'wikilinks': [
                                    ('base_url', '/'+project+'/wiki/'), 
                                    ('end_url', ''),
                                    ('html_class', '') ]},
        safe_mode = True
    )
    res = mark_safe(res)
    return res
