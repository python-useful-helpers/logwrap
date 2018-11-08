#    Copyright 2018 Alexey Stepanov aka penguinolog

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

import inspect
import types
import typing


cdef bint _known_callable(item: typing.Any):
    """Check for possibility to parse callable."""
    return isinstance(item, (types.FunctionType, types.MethodType))


cdef bint _simple(item: typing.Any):
    """Check for nested iterations: True, if not."""
    return not isinstance(item, (list, set, tuple, dict, frozenset))


class ReprParameter:
    """Parameter wrapper wor repr and str operations over signature."""

    __slots__ = ("_value", "_parameter")

    POSITIONAL_ONLY = inspect.Parameter.POSITIONAL_ONLY
    POSITIONAL_OR_KEYWORD = inspect.Parameter.POSITIONAL_OR_KEYWORD
    VAR_POSITIONAL = inspect.Parameter.VAR_POSITIONAL
    KEYWORD_ONLY = inspect.Parameter.KEYWORD_ONLY
    VAR_KEYWORD = inspect.Parameter.VAR_KEYWORD

    empty = inspect.Parameter.empty

    def __init__(self, parameter: inspect.Parameter, value: typing.Optional[typing.Any] = None) -> None:
        """Parameter-like object store for repr and str tasks.

        :param parameter: parameter from signature
        :type parameter: inspect.Parameter
        :param value: default value override
        :type value: typing.Any
        """
        self._parameter = parameter
        self._value = value if value is not None else parameter.default

    @property
    def parameter(self) -> inspect.Parameter:
        """Parameter object."""
        return self._parameter

    @property
    def name(self) -> typing.Union[None, str]:
        """Parameter name.

        For `*args` and `**kwargs` add prefixes
        """
        if self.kind == inspect.Parameter.VAR_POSITIONAL:
            return "*" + self.parameter.name
        if self.kind == inspect.Parameter.VAR_KEYWORD:
            return "**" + self.parameter.name
        return self.parameter.name

    @property
    def value(self) -> typing.Any:
        """Parameter value to log.

        If function is bound to class -> value is class instance else default value.
        """
        return self._value

    @property
    def annotation(self) -> typing.Union[inspect.Parameter.empty, str]:
        """Parameter annotation."""
        return self.parameter.annotation

    @property
    def kind(self) -> int:
        """Parameter kind."""
        return self.parameter.kind  # type: ignore

    # noinspection PyTypeChecker
    def __hash__(self) -> int:
        """Block hashing.

        :raises TypeError: Not hashable.
        """
        msg = "unhashable type: '{0}'".format(self.__class__.__name__)
        raise TypeError(msg)

    def __repr__(self) -> str:
        """Debug purposes."""
        return '<{} "{}">'.format(self.__class__.__name__, self)


# pylint: disable=no-member
def _prepare_repr(func: typing.Union[types.FunctionType, types.MethodType]) -> typing.Iterator[ReprParameter]:
    """Get arguments lists with defaults."""
    ismethod = isinstance(func, types.MethodType)
    if not ismethod:
        real_func = func
    else:
        real_func = func.__func__  # type: ignore

    parameters = list(inspect.signature(real_func).parameters.values())

    params = iter(parameters)
    if ismethod and func.__self__ is not None:  # type: ignore
        try:
            yield ReprParameter(next(params), value=func.__self__)  # type: ignore
        except StopIteration:
            return
    for arg in params:
        yield ReprParameter(arg)


# pylint: enable=no-member


cdef class PrettyFormat:
    """Pretty Formatter.

    Designed for usage as __repr__ and __str__ replacement on complex objects
    """

    def __cinit__(self, unsigned int max_indent=20, unsigned int indent_step=4):
        """Pretty Formatter."""
        self.max_indent = max_indent
        self.indent_step = indent_step

    cdef int next_indent(self, unsigned int indent, unsigned int multiplier=1):
        """Next indentation value."""
        return indent + multiplier * self.indent_step

    cdef str _repr_callable(self, src: typing.Union[types.FunctionType, types.MethodType], unsigned int indent=0):
        """Repr callable object (function or method)."""
        raise NotImplementedError()

    cdef str _repr_simple(self, src: typing.Any, unsigned int indent=0, bint no_indent_start=False):
        """Repr object without iteration."""
        raise NotImplementedError()

    def _repr_dict_items(self, dict src, unsigned int indent=0) -> typing.Iterator[str]:  # type
        """Repr dict items."""
        raise NotImplementedError()

    cdef str _repr_iterable_item(self, bint nl, str obj_type, str prefix, unsigned int indent, str result, str suffix):
        """Repr iterable item."""
        raise NotImplementedError()

    def _repr_iterable_items(self, src: typing.Iterable, unsigned int indent=0) -> typing.Iterator[str]:
        """Repr iterable items (not designed for dicts)."""
        for elem in src:
            yield "\n" + self.process_element(src=elem, indent=self.next_indent(indent)) + ","

    def process_element(self, src: typing.Any, unsigned int indent=0, bint no_indent_start=False) -> str:
        """Make human readable representation of object."""
        cdef str prefix
        cdef str suffix
        cdef str result

        if hasattr(src, self._magic_method_name):
            result = getattr(src, self._magic_method_name)(self, indent=indent, no_indent_start=no_indent_start)
            return result  # type: ignore

        if _known_callable(src):
            return self._repr_callable(src=src, indent=indent)

        if _simple(src) or indent >= self.max_indent or not src:
            return self._repr_simple(src=src, indent=indent, no_indent_start=no_indent_start)

        if isinstance(src, dict):
            prefix, suffix = "{", "}"
            result = "".join(self._repr_dict_items(src=src, indent=indent))
        else:
            if isinstance(src, list):
                prefix, suffix = "[", "]"
            elif isinstance(src, tuple):
                prefix, suffix = "(", ")"
            else:
                prefix, suffix = "{", "}"
            result = "".join(self._repr_iterable_items(src=src, indent=indent))
        return self._repr_iterable_item(
            nl=no_indent_start,
            obj_type=src.__class__.__name__,
            prefix=prefix,
            indent=indent,
            result=result,
            suffix=suffix,
        )

    def __call__(self, src: typing.Any, unsigned int indent=0, bint no_indent_start=False) -> str:
        """Make human readable representation of object. The main entry point."""
        result = self.process_element(src, indent=indent, no_indent_start=no_indent_start)
        return result


cdef class PrettyRepr(PrettyFormat):
    """Pretty repr.

    Designed for usage as __repr__ replacement on complex objects
    """

    __slots__ = ()

    def __cinit__(self, unsigned int max_indent=20, unsigned int indent_step=4):
        self._magic_method_name = "__pretty_repr__"

    cdef str _strings_repr(self, unsigned int indent, val: typing.Union[bytes, str]):
        """Custom repr for strings and binary strings."""
        cdef str prefix

        if isinstance(val, bytes):
            val = val.decode(encoding="utf-8", errors="backslashreplace")
            prefix = "b"
        else:
            prefix = "u"
        return "{spc:<{indent}}{prefix}'''{string}'''".format(spc="", indent=indent, prefix=prefix, string=val)

    cdef str _repr_simple(self, src: typing.Any, unsigned int indent=0, bint no_indent_start=False):
        """Repr object without iteration."""
        indent = 0 if no_indent_start else indent
        if isinstance(src, set):
            return "{spc:<{indent}}{val}".format(spc="", indent=indent, val="set(" + " ,".join(map(repr, src)) + ")")
        if isinstance(src, (bytes, str)):
            return self._strings_repr(indent=indent, val=src)
        return "{spc:<{indent}}{val!r}".format(spc="", indent=indent, val=src)

    def _repr_dict_items(self, dict src, unsigned int indent=0) -> typing.Iterator[str]:
        """Repr dict items."""
        cdef unsigned int max_len = max((len(repr(key)) for key in src)) if src else 0

        for key, val in src.items():
            yield "\n{spc:<{indent}}{key!r:{size}}: {val},".format(
                spc="",
                indent=self.next_indent(indent),
                size=max_len,
                key=key,
                val=self.process_element(val, indent=self.next_indent(indent, multiplier=2), no_indent_start=True),
            )

    cdef str _repr_callable(self, src: typing.Union[types.FunctionType, types.MethodType], unsigned int indent=0):
        """Repr callable object (function or method)."""
        cdef str param_str = ""
        cdef str annotation

        for param in _prepare_repr(src):
            param_str += "\n{spc:<{indent}}{param.name}".format(spc="", indent=self.next_indent(indent), param=param)
            if param.annotation is not param.empty:
                param_str += ": {param.annotation}".format(param=param)
            if param.value is not param.empty:
                param_str += "={val}".format(
                    val=self.process_element(src=param.value, indent=indent, no_indent_start=True)
                )
            param_str += ","

        if param_str:
            param_str += "\n" + " " * indent

        sig = inspect.signature(src)
        if sig.return_annotation is inspect.Parameter.empty:
            annotation = ""
        else:
            annotation = " -> {sig.return_annotation!r}".format(sig=sig)

        return "\n{spc:<{indent}}<{obj!r} with interface ({args}){annotation}>".format(
            spc="", indent=indent, obj=src, args=param_str, annotation=annotation
        )

    cdef str _repr_iterable_item(self, bint nl, str obj_type, str prefix, unsigned int indent, str result, str suffix):
        """Repr iterable item."""
        return (
            "{nl}"
            "{spc:<{indent}}{obj_type:}({prefix}{result}\n"
            "{spc:<{indent}}{suffix})".format(
                nl="\n" if nl else "",
                spc="",
                indent=indent,
                obj_type=obj_type,
                prefix=prefix,
                result=result,
                suffix=suffix,
            )
        )


cdef class PrettyStr(PrettyFormat):
    """Pretty str."""

    def __cinit__(self, unsigned int max_indent=20, unsigned int indent_step=4):
        self._magic_method_name = "__pretty_str__"

    cdef str _strings_str(self, unsigned int indent, val: typing.Union[bytes, str]):
        """Custom repr for strings and binary strings."""
        if isinstance(val, bytes):
            val = val.decode(encoding="utf-8", errors="backslashreplace")
        return "{spc:<{indent}}{string}".format(spc="", indent=indent, string=val)

    cdef str _repr_simple(self, src: typing.Any, unsigned int indent=0, bint no_indent_start=False):
        """Repr object without iteration."""
        indent = 0 if no_indent_start else indent
        if isinstance(src, set):
            return "{spc:<{indent}}{val}".format(spc="", indent=indent, val="set(" + " ,".join(map(str, src)) + ")")
        if isinstance(src, (bytes, str)):
            return self._strings_str(indent=indent, val=src)
        return "{spc:<{indent}}{val!s}".format(spc="", indent=indent, val=src)

    def _repr_dict_items(self, dict src, unsigned int indent=0) -> typing.Iterator[str]:
        """Repr dict items."""
        cdef unsigned int max_len = max((len(str(key)) for key in src)) if src else 0
        for key, val in src.items():
            yield "\n{spc:<{indent}}{key!s:{size}}: {val},".format(
                spc="",
                indent=self.next_indent(indent),
                size=max_len,
                key=key,
                val=self.process_element(val, indent=self.next_indent(indent, multiplier=2), no_indent_start=True),
            )

    cdef str _repr_callable(self, src: typing.Union[types.FunctionType, types.MethodType], unsigned int indent=0):
        """Repr callable object (function or method)."""
        cdef str param_str = ""
        cdef str annotation

        for param in _prepare_repr(src):
            param_str += "\n{spc:<{indent}}{param.name}".format(spc="", indent=self.next_indent(indent), param=param)
            if param.annotation is not param.empty:
                param_str += ": {param.annotation}".format(param=param)
            if param.value is not param.empty:
                param_str += "={val}".format(
                    val=self.process_element(src=param.value, indent=indent, no_indent_start=True)
                )
            param_str += ","

        if param_str:
            param_str += "\n" + " " * indent

        sig = inspect.signature(src)
        if sig.return_annotation is inspect.Parameter.empty:
            annotation = ""
        else:
            annotation = " -> {sig.return_annotation!r}".format(sig=sig)

        return "\n{spc:<{indent}}<{obj!s} with interface ({args}){annotation}>".format(
            spc="", indent=indent, obj=src, args=param_str, annotation=annotation
        )

    cdef str _repr_iterable_item(self, bint nl, str obj_type, str prefix, unsigned int indent, str result, str suffix):
        """Repr iterable item."""
        return (
            "{nl}"
            "{spc:<{indent}}{prefix}{result}\n"
            "{spc:<{indent}}{suffix}".format(
                nl="\n" if nl else "", spc="", indent=indent, prefix=prefix, result=result, suffix=suffix
            )
        )


def pretty_repr(
    src: typing.Any,
    unsigned int indent=0,
    bint no_indent_start=False,
    unsigned int max_indent=20,
    unsigned int indent_step=4
) -> str:
    """Make human readable repr of object."""
    return PrettyRepr(max_indent=max_indent, indent_step=indent_step)(
        src=src, indent=indent, no_indent_start=no_indent_start
    )


def pretty_str(
    src: typing.Any,
    unsigned int indent=0,
    bint no_indent_start=False,
    unsigned int max_indent=20,
    unsigned int indent_step=4
) -> str:
    """Make human readable str of object."""
    return PrettyStr(max_indent=max_indent, indent_step=indent_step)(
        src=src, indent=indent, no_indent_start=no_indent_start
    )
