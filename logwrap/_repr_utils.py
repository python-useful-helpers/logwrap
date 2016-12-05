#    Copyright 2016 Alexey Stepanov aka penguinolog

#    Copyright 2016 Mirantis, Inc.

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
import types

# pylint: disable=ungrouped-imports, no-name-in-module
if sys.version_info[0:2] > (3, 0):
    from inspect import Parameter
    from inspect import signature
else:
    # noinspection PyUnresolvedReferences
    from funcsigs import Parameter
    # noinspection PyUnresolvedReferences
    from funcsigs import signature
# pylint: enable=ungrouped-imports, no-name-in-module


if sys.version_info[0:2] > (3, 0):
    binary_type = bytes
    text_type = str
else:
    binary_type = str
    # pylint: disable=unicode-builtin, undefined-variable
    # noinspection PyUnresolvedReferences
    text_type = unicode  # NOQA
    # pylint: enable=unicode-builtin, undefined-variable


def _simple(item):
    """Check for nested iterations: True, if not"""
    return not isinstance(item, (list, set, tuple, dict))


def _strings_repr(indent, val):
    """Custom repr for strings and binary strings"""
    if isinstance(val, binary_type):
        val = val.decode(
            encoding='utf-8',
            errors='backslashreplace'
        )
        prefix = 'b'
    else:
        prefix = 'u'
    return "{spc:<{indent}}{prefix}'''{string}'''".format(
        spc='',
        indent=indent,
        prefix=prefix,
        string=val
    )


def _set_repr(indent, val):
    """Custom repr formatter for sets"""
    return "{spc:<{indent}}{val}".format(
        spc='',
        indent=indent,
        val="set({})".format(
            ' ,'.join(
                map(
                    '{!r}'.format,  # unicode -> !repr
                    val
                )
            )
        )
    )


repr_formatters = {
    'simple': "{spc:<{indent}}{val!r}".format,
    'manual': "{spc:<{indent}}{val}".format,
    'simple_set': _set_repr,
    'text': _strings_repr,
    'dict': "\n{spc:<{indent}}{key!r:{size}}: {val},".format,
    'iterable_item':
        "\n"
        "{spc:<{indent}}{obj_type:}({start}{result}\n"
        "{spc:<{indent}}{end})".format,
    'callable': "\n{spc:<{indent}}<{obj!r} with interface ({args})>".format,
    'func_arg': "\n{spc:<{indent}}{key},".format,
    'func_def_arg': "\n{spc:<{indent}}{key}={val},".format,
}


# pylint: disable=no-member
def prepare_repr(func):
    """Get arguments lists with defaults

    :type func: union(types.FunctionType, types.MethodType)
    :rtype: generator
    """
    isfunction = isinstance(func, types.FunctionType)
    real_func = func if isfunction else func.__func__

    parameters = list(signature(real_func).parameters.values())

    params = iter(parameters)
    if not isfunction and func.__self__ is not None:
        yield next(params).name, func.__self__
    for arg in params:
        if arg.default != Parameter.empty:
            yield arg.name, arg.default
        elif arg.kind == Parameter.VAR_POSITIONAL:
            yield '*' + arg.name
        elif arg.kind == Parameter.VAR_KEYWORD:
            yield '**' + arg.name
        else:
            yield arg.name
# pylint: enable=no-member


class PrettyFormat(object):
    """Pretty Formatter

    Designed for usage as __repr__ and __str__ replacement on complex objects
    """

    def __init__(
        self,
        formatters=None,
        max_indent=20,
        indent_step=4,
    ):
        """Pretty Formatter

        :param formatters: object formatters (prepared str.format functions)
        :type formatters: {str: callable}
        :param max_indent: maximal indent before classic repr() call
        :type max_indent: int
        :param indent_step: step for the next indentation level
        :type indent_step: int
        """
        if formatters is None:
            formatters = repr_formatters
        self.__formatters = formatters
        self.__max_indent = max_indent
        self.__indent_step = indent_step

    @property
    def max_indent(self):
        """Max indent getter

        :rtype: int
        """
        return self.__max_indent

    @property
    def indent_step(self):
        """Indent step getter

        :rtype: int
        """
        return self.__indent_step

    def next_indent(self, indent, doubled=False):
        """Next indentation value

        :param indent: current indentation value
        :type indent: int
        :param doubled: use double step instead of single
        :type doubled: bool
        :rtype: int
        """
        mult = 1 if not doubled else 2
        return indent + mult * self.indent_step

    def _repr_callable(self, src, indent=0):
        """repr callable object (function or method)

        :type src: union(types.FunctionType, types.MethodType)
        :type indent: int
        :rtype: str
        """
        param_str = ""

        for param in prepare_repr(src):
            if isinstance(param, tuple):
                param_str += self.__formatters['func_def_arg'](
                    spc='',
                    indent=self.next_indent(indent),
                    key=param[0],
                    val=self.process(
                        src=param[1],
                        indent=indent,
                        no_indent_start=True,
                    )
                )
            else:
                param_str += self.__formatters['func_arg'](
                    spc='',
                    indent=self.next_indent(indent),
                    key=param
                )

        if param_str:
            param_str += "\n" + " " * indent
        return self.__formatters['callable'](
            spc="",
            indent=indent,
            obj=src,
            args=param_str,
        )

    def _repr_simple(self, src, indent=0, no_indent_start=False):
        """repr object without iteration

        :type src: union(six.binary_type, six.text_type, int, iterable, object)
        :type indent: int
        :type no_indent_start: bool
        :rtype: str
        """
        if isinstance(src, (types.FunctionType, types.MethodType)):
            return self._repr_callable(
                src=src,
                indent=indent,
            )
        indent = 0 if no_indent_start else indent
        if isinstance(src, (binary_type, text_type)):
            return self.__formatters['text'](
                indent=indent,
                val=src
            )
        # Parse set manually due to different repr() implementation
        # in different python versions
        if isinstance(src, set):
            return self.__formatters['simple_set'](
                indent=indent,
                val=src,
            )
        return self.__formatters['simple'](
            spc='',
            indent=indent,
            val=src,
        )

    def process(self, src, indent=0, no_indent_start=False):
        """Make human readable representation of object

        :param src: object to process
        :type src: union(six.binary_type, six.text_type, int, iterable, object)
        :param indent: start indentation, all next levels is +4
        :type indent: int
        :param no_indent_start:
            do not indent open bracket and simple parameters
        :type no_indent_start: bool
        :return: formatted string
        """
        if _simple(src) or indent >= self.max_indent or len(src) == 0:
            return self._repr_simple(
                src=src,
                indent=indent,
                no_indent_start=no_indent_start,
            )
        result = ''
        if isinstance(src, dict):
            prefix, suffix = '{', '}'
            max_len = len(max([repr(key) for key in src])) if src else 0
            for key, val in src.items():
                result += self.__formatters['dict'](
                    spc='',
                    indent=self.next_indent(indent),
                    size=max_len,
                    key=key,
                    val=self.process(
                        val,
                        self.next_indent(indent, doubled=True),
                        no_indent_start=True,
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
                if _simple(elem) or\
                        len(elem) == 0 or \
                        self.next_indent(indent) >= self.max_indent:
                    result += '\n'
                result += self.process(
                    elem,
                    self.next_indent(indent),
                ) + ','
        return (
            self.__formatters['iterable_item'](
                spc='',
                obj_type=src.__class__.__name__,
                start=prefix,
                indent=indent,
                result=result,
                end=suffix,
            )
        )


def pretty_repr(
    src,
    indent=0,
    no_indent_start=False,
    max_indent=20,
    indent_step=4,
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
    :param indent_step: step for the next indentation level
    :type indent_step: int
    :return: formatted string
    """
    return PrettyFormat(
        formatters=repr_formatters,
        max_indent=max_indent,
        indent_step=indent_step
    ).process(
        src=src,
        indent=indent,
        no_indent_start=no_indent_start,
    )


__all__ = ['pretty_repr']
