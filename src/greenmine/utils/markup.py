# -*- coding: utf-8 -*-

import sys
import codecs

from docutils import nodes
from docutils.parsers.rst import Directive

def parselinenos(spec, total):
    """Parse a line number spec (such as "1,2,4-6") and return a list of
    wanted line numbers.
    """
    items = list()
    parts = spec.split(',')
    for part in parts:
        try:
            begend = part.strip().split('-')
            if len(begend) > 2:
                raise ValueError
            if len(begend) == 1:
                items.append(int(begend[0])-1)
            else:
                start = (begend[0] == '') and 0 or int(begend[0])-1
                end = (begend[1] == '') and total or int(begend[1])
                items.extend(xrange(start, end))
        except Exception:
            raise ValueError('invalid line number spec: %r' % spec)
    return items

def set_source_info(directive, node):
    node.source, node.line = \
        directive.state_machine.get_source_and_line(directive.lineno)


class CodeBlock(Directive):
    """
    Directive for a code block with special highlighting or line numbering
    settings.
    """

    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'linenos': directives.flag,
        'emphasize-lines': directives.unchanged_required,
    }

    def run(self):
        code = u'\n'.join(self.content)

        linespec = self.options.get('emphasize-lines')
        if linespec:
            try:
                nlines = len(self.content)
                hl_lines = [x+1 for x in parselinenos(linespec, nlines)]
            except ValueError, err:
                document = self.state.document
                return [document.reporter.warning(str(err), line=self.lineno)]
        else:
            hl_lines = None

        literal = nodes.literal_block(code, code)
        literal['language'] = self.arguments[0]
        literal['linenos'] = 'linenos' in self.options
        if hl_lines is not None:
            literal['highlight_args'] = {'hl_lines': hl_lines}
        set_source_info(self, literal)
        return [literal]
