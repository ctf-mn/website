from datetime import UTC, datetime
import re

from jinja2.ext import Extension


def utcnow():
    return datetime.now(UTC).replace(tzinfo=None)


class Form:
    """ Updated at 2024-02-04 """
    def __init__(self, form):
        self.value = form.copy()
        self.error = {}
        self.validated = False

    def __getitem__(self, key):
        return self.value[key]

    def is_valid(self):
        if not self.validated:
            self.validate()
        for k in self.error.keys():
            assert k in self.value
        return not self.error


class JinjaExt(Extension):
    """ Updated at 2024-02-04 """
    def preprocess(self, source, name, filename=None):
        #  Usage: `%def Form()`
        if source.startswith('%def\n') and name.startswith('Macros/'):
            macro_name = name.rsplit('/', 1)[1].split('.', 1)[0]
            head, tail = source.split('\n', 1)
            head = f'%macro {macro_name}()'
            result = head + '\n' + tail
            return result + '\n%endmacro'

        #  Usage: `%def Form(action='')
        if source.startswith('%def ') and name.startswith('Macros/'):
            macro_name = name.rsplit('/', 1)[1].split('.', 1)[0]
            head, tail = source.split('\n', 1)
            head = head.replace('%def ', f'%macro {macro_name}(')
            head = head + ')'
            result = head + '\n' + tail
            return result + '\n%endmacro'
        # endfold

        source = re.sub(r'%use ([a-zA-Z0-9]+)', r"{% from 'Macros/\1.html' import \1 with context %}{% set \1=\1 %}", source)

        # inline
        source = re.sub(r'<([A-Z][a-zA-Z0-9]+) />', r'{{ ui.\1() }}', source)
        source = re.sub(r'<([A-Z][a-zA-Z0-9]+) ([^\n\/]+) />', r'{{ ui.\1(\2) }}', source)

        # multi-line
        source = re.sub(r'<([A-Z][a-zA-Z0-9]+)>', r'%call ui.\1()', source)
        source = re.sub(r'<([A-Z][a-zA-Z0-9]+) ([^\n>]+)>', r'%call ui.\1(\2)', source)
        source = re.sub(r'</([A-Z][a-zA-Z0-9]+)>', r'%endcall', source)

        result = ''
        for line in source.split('\n'):
            if re.search(r' ui\.[A-Z][a-zA-Z0-9]+(.+)', line):
                head = line.split('(', 1)[0] + '('
                tail = ')' + line.rsplit(')', 1)[1]
                body = line[len(head):-len(tail)]
                # print('DEBUG:', repr(body))
                body = re.sub(r'([a-z_]+)="([^"]*)" ', r'\1="\2", ', body)
                body = re.sub(r'([a-z_]+) ', r'\1, ', body)
                # print('DEBUG:', repr(body))
                parts = []
                for p in body.split(', '):
                    if p and '=' not in p:
                        p = p + '=true'
                    parts.append(p)
                body = ', '.join(parts)
                line = head + body + tail
                # print('DEBUG:', line)
            result += line + '\n'

        # print('DEBUG result:', result)
        return result
