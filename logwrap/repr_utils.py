#    Copyright 2016 Mirantis, Inc.
#    Copyright 2016 Alexey Stepanov aka penguinolog
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""repr_utils module

This is no reason to import this submodule directly, all required methods is
available from the main module.
"""

from __future__ import absolute_import
from __future__ import unicode_literals

import sys


if sys.version_info[0:2] > (3, 0):
    binary_type = bytes
    text_type = str
else:
    binary_type = str
    # pylint: disable=unicode-builtin
    # noinspection PyUnresolvedReferences
    text_type = unicode  # NOQA
    # pylint: enable=unicode-builtin


def _simple(item):
    """Check for nested iterations: True, if not"""
    return not isinstance(item, (list, set, tuple, dict))

_formatters = {
    'simple': "{spc:<{indent}}{val!r}".format,
    'manual': "{spc:<{indent}}{val}".format,
    'text': "{spc:<{indent}}{prefix}'''{string}'''".format,
    'dict': "\n{spc:<{indent}}{key!r:{size}}: {val},".format,
    'iterable_item':
        "\n"
        "{spc:<{indent}}{obj_type:}({start}{result}\n"
        "{spc:<{indent}}{end})".format
}


def _repr_simple(src, indent=0, no_indent_start=False):
    """repr object without iteration

    :type src: union(six.binary_type, six.text_type, int, iterable, object)
    :type indent: int
    :type no_indent_start: bool
    :rtype: str
    """
    indent = 0 if no_indent_start else indent
    if isinstance(src, (binary_type, text_type)):
        if isinstance(src, binary_type):
            string = src.decode(
                encoding='utf-8',
                errors='backslashreplace'
            )
            prefix = 'b'
        else:
            string = src
            prefix = 'u'
        return _formatters['text'](
            spc='',
            indent=indent,
            prefix=prefix,
            string=string
        )
    # Parse set manually due to different repr() implementation
    # in different python versions
    if isinstance(src, set):
        return _formatters['manual'](
            spc='',
            indent=indent,
            val='set()',
        )
    return _formatters['simple'](
        spc='',
        indent=indent,
        val=src,
    )


def pretty_repr(
        src,
        indent=0,
        no_indent_start=False,
        max_indent=20,
):
    """Make human readable repr of object

    :param src: object to process
    :type src: union(six.binary_type, six.text_type, int, iterable, object)
    :param indent: start indentation, all next levels is +4
    :type indent: int
    :param no_indent_start: do not indent open bracket and simple parameters
    :type no_indent_start: bool
    :param max_indent: maximal indent before classic repr() call
    :type max_indent: int
    :return: formatted string
    """
    if _simple(src) or indent >= max_indent or len(src) == 0:
        return _repr_simple(
            src=src,
            indent=indent,
            no_indent_start=no_indent_start,
        )
    result = ''
    if isinstance(src, dict):
        prefix, suffix = '{', '}'
        max_len = len(max([repr(key) for key in src])) if src else 0
        for key, val in src.items():
            result += _formatters['dict'](
                spc='',
                indent=indent + 4,
                size=max_len,
                key=key,
                val=pretty_repr(
                    val,
                    indent + 8,
                    no_indent_start=True,
                    max_indent=max_indent,
                )
            )
    else:
        if isinstance(src, list):
            prefix, suffix = '[', ']'
        elif isinstance(src, tuple):
            prefix, suffix = '(', ')'
        else:
            prefix, suffix = '{', '}'
        for elem in src:
            if _simple(elem) or len(elem) == 0 or indent + 4 >= max_indent:
                result += '\n'
            result += pretty_repr(
                elem,
                indent + 4,
                max_indent=max_indent,
            ) + ','
    return (
        _formatters['iterable_item'](
            spc='',
            obj_type=src.__class__.__name__,
            start=prefix,
            indent=indent,
            result=result,
            end=suffix,
        )
    )

__all__ = ['pretty_repr']
