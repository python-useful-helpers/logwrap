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
if six.PY3:  # pragma: no cover
    from inspect import (
        Parameter,
        signature,
    )
else:  # pragma: no cover
    # noinspection PyUnresolvedReferences
    from funcsigs import (
        Parameter,
        signature,
    )
# pylint: enable=ungrouped-imports, no-name-in-module


def _known_callable(item):
    """Check for possibility to parse callable."""
    return isinstance(item, (types.FunctionType, types.MethodType))


def _simple(item):
    """Check for nested iterations: True, if not."""
    return not isinstance(item, (list, set, tuple, dict, frozenset))


# pylint: disable=no-member
def _prepare_repr(func):
    """Get arguments lists with defaults.

    :type func: typing.Union[types.FunctionType, types.MethodType]
    :rtype: typing.Generator[str]
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

    __slots__ = (
        '__max_indent',
        '__indent_step',
        '__py2_str',
    )

    def __init__(
        self,
        max_indent=20,
        indent_step=4,
        py2_str=False,
    ):
        """Pretty Formatter.

        :param max_indent: maximal indent before classic repr() call
        :type max_indent: int
        :param indent_step: step for the next indentation level
        :type indent_step: int
        :param py2_str: use Python 2.x compatible strings instead of unicode
        :type py2_str: bool
        """
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

        :type src: typing.Union[types.FunctionType, types.MethodType]
        :type indent: int
        :rtype: str
        """
        raise NotImplementedError  # pragma: no cover

    def _repr_simple(self, src, indent=0, no_indent_start=False):
        """Repr object without iteration.

        :type src: typing.Union[
                   six.binary_type, six.text_type, int, typing.Iterable,
                   object,
                   ]
        :type indent: int
        :type no_indent_start: bool
        :rtype: str
        """
        raise NotImplementedError()  # pragma: no cover

    def _repr_dict_items(self, src, indent=0):
        """Repr dict items.

        :param src: object to process
        :type src: dict
        :param indent: start indentation
        :type indent: int
        :rtype: typing.Generator[str]
        """
        raise NotImplementedError()  # pragma: no cover

    @staticmethod
    def _repr_iterable_item(
        nl,
        obj_type,
        prefix,
        indent,
        result,
        suffix,
    ):
        """Repr iterable item.

        :param nl: newline before item
        :type nl: bool
        :param obj_type: Object type
        :type obj_type: str
        :param prefix: prefix
        :type prefix: str
        :param indent: start indentation
        :type indent: int
        :param result: result of pre-formatting
        :type result: str
        :param suffix: suffix
        :type suffix: str
        :rtype: str
        """
        raise NotImplementedError()  # pragma: no cover

    def _repr_iterable_items(self, src, indent=0):
        """Repr iterable items (not designed for dicts).

        :param src: object to process
        :type src: typing.Iterable
        :param indent: start indentation
        :type indent: int
        :rtype: typing.Generator[str]
        """
        for elem in src:
            yield '\n' + self.process_element(
                src=elem,
                indent=self.next_indent(indent),
            ) + ','

    @property
    def _magic_method_name(self):
        """Magic method name.

        :rtype: str
        """
        raise NotImplementedError  # pragma: no cover

    def process_element(self, src, indent=0, no_indent_start=False):
        """Make human readable representation of object.

        :param src: object to process
        :type src: typing.Union[
                   six.binary_type, six.text_type, int, typing.Iterable, object
                   ]
        :param indent: start indentation
        :type indent: int
        :param no_indent_start:
            do not indent open bracket and simple parameters
        :type no_indent_start: bool
        :return: formatted string
        :rtype: six.text_type
        """
        if hasattr(src, self._magic_method_name):
            return getattr(
                src,
                self._magic_method_name
            )(
                self,
                indent=indent,
                no_indent_start=no_indent_start
            )

        if _known_callable(src):
            return self._repr_callable(
                src=src,
                indent=indent,
            )

        if _simple(src) or indent >= self.max_indent or not src:
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
            self._repr_iterable_item(
                nl=no_indent_start,
                obj_type=src.__class__.__name__,
                prefix=prefix,
                indent=indent,
                result=result,
                suffix=suffix,
            )
        )

    def __call__(
        self,
        src,
        indent=0,
        no_indent_start=False
    ):
        """Make human readable representation of object. The main entry point.

        :param src: object to process
        :type src: typing.Union[
                   six.binary_type, six.text_type, int, typing.Iterable, object
                   ]
        :param indent: start indentation
        :type indent: int
        :param no_indent_start:
            do not indent open bracket and simple parameters
        :type no_indent_start: bool
        :return: formatted string
        :rtype: str
        """
        result = self.process_element(
            src,
            indent=indent,
            no_indent_start=no_indent_start
        )
        if self.__py2_str:  # pragma: no cover
            return result.encode(
                encoding='utf-8',
                errors='backslashreplace',
            )
        return result


class PrettyRepr(PrettyFormat):
    """Pretty repr.

    Designed for usage as __repr__ replacement on complex objects
    """

    __slots__ = ()

    @property
    def _magic_method_name(self):
        """Magic method name.

        :rtype: str
        """
        return '__pretty_repr__'

    @staticmethod
    def _strings_repr(indent, val):
        """Custom repr for strings and binary strings."""
        if isinstance(val, six.binary_type):
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

    def _repr_simple(self, src, indent=0, no_indent_start=False):
        """Repr object without iteration.

        :type src: typing.Union[
                   six.binary_type, six.text_type, int, typing.Iterable,
                   object,
                   ]
        :type indent: int
        :type no_indent_start: bool
        :rtype: str
        """
        indent = 0 if no_indent_start else indent
        if isinstance(src, set):
            return "{spc:<{indent}}{val}".format(
                spc='',
                indent=indent,
                val="set(" + ' ,'.join(map(repr, src)) + ")"
            )
        if isinstance(src, (six.binary_type, six.text_type)):
            return self._strings_repr(indent=indent, val=src)
        return "{spc:<{indent}}{val!r}".format(
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
        :rtype: typing.Generator[str]
        """
        max_len = max((len(repr(key)) for key in src)) if src else 0
        for key, val in src.items():
            yield "\n{spc:<{indent}}{key!r:{size}}: {val},".format(
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

    def _repr_callable(self, src, indent=0):
        """Repr callable object (function or method).

        :type src: typing.Union[types.FunctionType, types.MethodType]
        :type indent: int
        :rtype: str
        """
        param_str = ""

        for param in _prepare_repr(src):
            if isinstance(param, tuple):
                param_str += "\n{spc:<{indent}}{key}={val},".format(
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
                param_str += "\n{spc:<{indent}}{key},".format(
                    spc='',
                    indent=self.next_indent(indent),
                    key=param
                )

        if param_str:
            param_str += "\n" + " " * indent
        return "\n{spc:<{indent}}<{obj!r} with interface ({args})>".format(
            spc="",
            indent=indent,
            obj=src,
            args=param_str,
        )

    @staticmethod
    def _repr_iterable_item(
        nl,
        obj_type,
        prefix,
        indent,
        result,
        suffix,
    ):
        """Repr iterable item.

        :param nl: newline before item
        :type nl: bool
        :param obj_type: Object type
        :type obj_type: str
        :param prefix: prefix
        :type prefix: str
        :param indent: start indentation
        :type indent: int
        :param result: result of pre-formatting
        :type result: str
        :param suffix: suffix
        :type suffix: str
        :rtype: str
        """
        return (
            "{nl}"
            "{spc:<{indent}}{obj_type:}({prefix}{result}\n"
            "{spc:<{indent}}{suffix})".format(
                nl='\n' if nl else '',
                spc='',
                indent=indent,
                obj_type=obj_type,
                prefix=prefix,
                result=result,
                suffix=suffix
            )
        )


class PrettyStr(PrettyFormat):
    """Pretty str.

    Designed for usage as __str__ replacement on complex objects
    """

    __slots__ = ()

    @property
    def _magic_method_name(self):
        """Magic method name.

        :rtype: str
        """
        return '__pretty_str__'

    @staticmethod
    def _strings_str(indent, val):
        """Custom repr for strings and binary strings."""
        if isinstance(val, six.binary_type):
            val = val.decode(
                encoding='utf-8',
                errors='backslashreplace'
            )
        return "{spc:<{indent}}{string}".format(
            spc='',
            indent=indent,
            string=val
        )

    def _repr_simple(self, src, indent=0, no_indent_start=False):
        """Repr object without iteration.

        :type src: typing.Union[
                   six.binary_type, six.text_type, int, typing.Iterable,
                   object,
                   ]
        :type indent: int
        :type no_indent_start: bool
        :rtype: str
        """
        indent = 0 if no_indent_start else indent
        if isinstance(src, set):
            return "{spc:<{indent}}{val}".format(
                spc='',
                indent=indent,
                val="set(" + ' ,'.join(map(str, src)) + ")"
            )
        if isinstance(src, (six.binary_type, six.text_type)):
            return self._strings_str(indent=indent, val=src)
        return "{spc:<{indent}}{val!s}".format(
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
        :rtype: typing.Generator[str]
        """
        max_len = max((len(str(key)) for key in src)) if src else 0
        for key, val in src.items():
            yield "\n{spc:<{indent}}{key!s:{size}}: {val},".format(
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

    def _repr_callable(self, src, indent=0):
        """Repr callable object (function or method).

        :type src: typing.Union[types.FunctionType, types.MethodType]
        :type indent: int
        :rtype: str
        """
        param_str = ""

        for param in _prepare_repr(src):
            if isinstance(param, tuple):
                param_str += "\n{spc:<{indent}}{key}={val},".format(
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
                param_str += "\n{spc:<{indent}}{key},".format(
                    spc='',
                    indent=self.next_indent(indent),
                    key=param
                )

        if param_str:
            param_str += "\n" + " " * indent
        return "\n{spc:<{indent}}<{obj!s} with interface ({args})>".format(
            spc="",
            indent=indent,
            obj=src,
            args=param_str,
        )

    @staticmethod
    def _repr_iterable_item(
        nl,
        obj_type,
        prefix,
        indent,
        result,
        suffix,
    ):
        """Repr iterable item.

        :param nl: newline before item
        :type nl: bool
        :param obj_type: Object type
        :type obj_type: str
        :param prefix: prefix
        :type prefix: str
        :param indent: start indentation
        :type indent: int
        :param result: result of pre-formatting
        :type result: str
        :param suffix: suffix
        :type suffix: str
        :rtype: str
        """
        return (
            "{nl}"
            "{spc:<{indent}}{prefix}{result}\n"
            "{spc:<{indent}}{suffix}".format(
                nl='\n' if nl else '',
                spc='',
                indent=indent,
                prefix=prefix,
                result=result,
                suffix=suffix
            )
        )


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
    :type src: typing.Union[
               six.binary_type, six.text_type, int, typing.Iterable, object
               ]
    :param indent: start indentation, all next levels is +indent_step
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
    :rtype: str
    """
    return PrettyRepr(
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
    :type src: typing.Union[
               six.binary_type, six.text_type, int, typing.Iterable, object
               ]
    :param indent: start indentation, all next levels is +indent_step
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
    return PrettyStr(
        max_indent=max_indent,
        indent_step=indent_step,
        py2_str=py2_str
    )(
        src=src,
        indent=indent,
        no_indent_start=no_indent_start,
    )


__all__ = (
    'PrettyFormat',
    'PrettyRepr',
    'PrettyStr',
    'pretty_repr',
    'pretty_str',
)
