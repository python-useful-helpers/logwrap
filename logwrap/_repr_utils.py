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

"""repr_utils module.

This is no reason to import this submodule directly, all required methods is
available from the main module.
"""

from __future__ import absolute_import
from __future__ import unicode_literals

import types

import six

# pylint: disable=ungrouped-imports, no-name-in-module
if six.PY3:
    from inspect import Parameter
    from inspect import signature
else:
    # noinspection PyUnresolvedReferences
    from funcsigs import Parameter
    # noinspection PyUnresolvedReferences
    from funcsigs import signature
# pylint: enable=ungrouped-imports, no-name-in-module

# pylint: disable=wrong-import-position
# noinspection PyProtectedMember
from logwrap._formatters import (  # noqa
    c_repr_formatters, s_repr_formatters,
    c_str_formatters, s_str_formatters
)
# pylint: enable=wrong-import-position


def _known_callble(item):
    """Check for possibility to parse callable."""
    return isinstance(item, (types.FunctionType, types.MethodType))


def _simple(item):
    """Check for nested iterations: True, if not."""
    return not isinstance(item, (list, set, tuple, dict))


# pylint: disable=no-member
def _prepare_repr(func):
    """Get arguments lists with defaults.

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
    """Pretty Formatter.

    Designed for usage as __repr__ and __str__ replacement on complex objects
    """

    def __init__(
        self,
        simple_formatters,
        complex_formatters,
        keyword='repr',
        max_indent=20,
        indent_step=4,
        py2_str=False,
    ):
        """Pretty Formatter.

        :param simple_formatters: object formatters by type
        :type simple_formatters: {str: callable}
        :param complex_formatters: object formatters for complex objects
        :type complex_formatters: {str: callable}
        :param keyword: operation keyword (__pretty_{keyword}__)
        :type keyword: str
        :param max_indent: maximal indent before classic repr() call
        :type max_indent: int
        :param indent_step: step for the next indentation level
        :type indent_step: int
        :param py2_str: use Python 2.x compatible strings instead of unicode
        :type py2_str: bool
        """
        self.__s_formatters = simple_formatters
        self.__c_formatters = complex_formatters
        self.__keyword = keyword
        self.__max_indent = max_indent
        self.__indent_step = indent_step
        self.__py2_str = py2_str and not six.PY3  # Python 2 only behavior

    @property
    def max_indent(self):
        """Max indent getter.

        :rtype: int
        """
        return self.__max_indent

    @property
    def indent_step(self):
        """Indent step getter.

        :rtype: int
        """
        return self.__indent_step

    def next_indent(self, indent, multiplier=1):
        """Next indentation value.

        :param indent: current indentation value
        :type indent: int
        :param multiplier: step multiplier
        :type multiplier: int
        :rtype: int
        """
        return indent + multiplier * self.indent_step

    def _repr_callable(self, src, indent=0):
        """Repr callable object (function or method).

        :type src: union(types.FunctionType, types.MethodType)
        :type indent: int
        :rtype: str
        """
        param_str = ""

        for param in _prepare_repr(src):
            if isinstance(param, tuple):
                param_str += self.__c_formatters['func_def_arg'](
                    spc='',
                    indent=self.next_indent(indent),
                    key=param[0],
                    val=self.process_element(
                        src=param[1],
                        indent=indent,
                        no_indent_start=True,
                    )
                )
            else:
                param_str += self.__c_formatters['func_arg'](
                    spc='',
                    indent=self.next_indent(indent),
                    key=param
                )

        if param_str:
            param_str += "\n" + " " * indent
        return self.__c_formatters['callable'](
            spc="",
            indent=indent,
            obj=src,
            args=param_str,
        )

    def _repr_simple(self, src, indent=0, no_indent_start=False):
        """Repr object without iteration.

        :type src: union(six.binary_type, six.text_type, int, iterable, object)
        :type indent: int
        :type no_indent_start: bool
        :rtype: str
        """
        indent = 0 if no_indent_start else indent
        # pylint: disable=unidiomatic-typecheck
        # We use type(obj) as dict key
        if type(src) in self.__s_formatters:
            return self.__s_formatters[type(src)](
                indent=indent,
                val=src
            )
        # pylint: enable=unidiomatic-typecheck
        return self.__s_formatters['default'](
            spc='',
            indent=indent,
            val=src,
        )

    def _repr_dict_items(self, src, indent=0):
        """Repr dict items.

        :param src: object to process
        :type src: dict
        :param indent: start indentation
        :type indent: int
        :rtype: generator
        """
        max_len = max([len(repr(key)) for key in src]) if src else 0
        for key, val in src.items():
            yield self.__c_formatters['dict'](
                spc='',
                indent=self.next_indent(indent),
                size=max_len,
                key=key,
                val=self.process_element(
                    val,
                    indent=self.next_indent(indent, multiplier=2),
                    no_indent_start=True,
                )
            )

    def _repr_iterable_items(self, src, indent=0):
        """Repr iterable items (not designed for dicts).

        :param src: object to process
        :type src: dict
        :param indent: start indentation
        :type indent: int
        :rtype: generator
        """
        for elem in src:
            yield '\n' + self.process_element(
                src=elem,
                indent=self.next_indent(indent),
            ) + ','

    def process_element(self, src, indent=0, no_indent_start=False):
        """Make human readable representation of object.

        :param src: object to process
        :type src: union(six.binary_type, six.text_type, int, iterable, object)
        :param indent: start indentation
        :type indent: int
        :param no_indent_start:
            do not indent open bracket and simple parameters
        :type no_indent_start: bool
        :return: formatted string
        :rtype: str
        """
        if hasattr(src, '__pretty_{}__'.format(self.__keyword)):
            return getattr(
                src,
                '__pretty_{}__'.format(self.__keyword)
            )(
                self,
                indent=indent,
                no_indent_start=no_indent_start
            )

        if _known_callble(src):
            return self._repr_callable(
                src=src,
                indent=indent,
            )

        if _simple(src) or indent >= self.max_indent or len(src) == 0:
            return self._repr_simple(
                src=src,
                indent=indent,
                no_indent_start=no_indent_start,
            )

        if isinstance(src, dict):
            prefix, suffix = '{', '}'
            result = ''.join(self._repr_dict_items(src=src, indent=indent))
        else:
            if isinstance(src, list):
                prefix, suffix = '[', ']'
            elif isinstance(src, tuple):
                prefix, suffix = '(', ')'
            else:
                prefix, suffix = '{', '}'
            result = ''.join(self._repr_iterable_items(src=src, indent=indent))
        return (
            self.__c_formatters['iterable_item'](
                nl='\n' if no_indent_start else '',
                spc='',
                obj_type=src.__class__.__name__,
                start=prefix,
                indent=indent,
                result=result,
                end=suffix,
            )
        )

    def __call__(
        self,
        src,
        indent=0,
        no_indent_start=False
    ):
        """Make human readable representation of object.

        :param src: object to process
        :type src: union(six.binary_type, six.text_type, int, iterable, object)
        :param indent: start indentation
        :type indent: int
        :param no_indent_start:
            do not indent open bracket and simple parameters
        :type no_indent_start: bool
        :return: formatted string
        """
        result = self.process_element(
            src,
            indent=indent,
            no_indent_start=no_indent_start
        )
        if self.__py2_str:
            return result.encode(
                encoding='utf-8',
                errors='backslashreplace',
            )
        return result


def pretty_repr(
    src,
    indent=0,
    no_indent_start=False,
    max_indent=20,
    indent_step=4,
    py2_str=False,
):
    """Make human readable repr of object.

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
    :param py2_str: use Python 2.x compatible strings instead of unicode
    :type py2_str: bool
    :return: formatted string
    """
    return PrettyFormat(
        simple_formatters=s_repr_formatters,
        complex_formatters=c_repr_formatters,
        keyword='repr',
        max_indent=max_indent,
        indent_step=indent_step,
        py2_str=py2_str
    )(
        src=src,
        indent=indent,
        no_indent_start=no_indent_start,
    )


def pretty_str(
    src,
    indent=0,
    no_indent_start=False,
    max_indent=20,
    indent_step=4,
    py2_str=False,
):
    """Make human readable str of object.

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
    :param py2_str: use Python 2.x compatible strings instead of unicode
    :type py2_str: bool
    :return: formatted string
    """
    return PrettyFormat(
        simple_formatters=s_str_formatters,
        complex_formatters=c_str_formatters,
        keyword='str',
        max_indent=max_indent,
        indent_step=indent_step,
        py2_str=py2_str
    )(
        src=src,
        indent=indent,
        no_indent_start=no_indent_start,
    )


__all__ = ('PrettyFormat', 'pretty_repr', 'pretty_str')
