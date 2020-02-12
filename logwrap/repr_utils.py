#    Copyright 2016 - 2020 Alexey Stepanov aka penguinolog

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

__all__ = ("PrettyFormat", "PrettyRepr", "PrettyStr", "pretty_repr", "pretty_str")

# Standard Library
import abc
import inspect
import types
import typing


def _known_callable(item: typing.Any) -> bool:
    """Check for possibility to parse callable.

    :param item:  item to check for repr() way
    :type item: typing.Any
    :return: item is callable and should be processed not using repr
    :rtype: bool
    """
    return isinstance(item, (types.FunctionType, types.MethodType))


def _simple(item: typing.Any) -> bool:
    """Check for nested iterations: True, if not.

    :param item: item to check for repr() way
    :type item: typing.Any
    :return: use repr() iver item by default
    :rtype: bool
    """
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

    def __init__(self, parameter: inspect.Parameter, value: typing.Any = inspect.Parameter.empty) -> None:
        """Parameter-like object store for repr and str tasks.

        :param parameter: parameter from signature
        :type parameter: inspect.Parameter
        :param value: default value override
        :type value: typing.Any
        """
        self._parameter: inspect.Parameter = parameter
        self._value: typing.Any = value if value is not parameter.empty else parameter.default

    @property
    def parameter(self) -> inspect.Parameter:
        """Parameter object.

        :return: original inspect.Parameter object
        :rtype: inspect.Parameter
        """
        return self._parameter

    @property
    def name(self) -> typing.Union[None, str]:
        """Parameter name.

        :return: parameter name. For `*args` and `**kwargs` add corresponding prefixes
        :rtype: typing.Union[None, str]
        """
        if self.kind == inspect.Parameter.VAR_POSITIONAL:
            return "*" + self.parameter.name
        if self.kind == inspect.Parameter.VAR_KEYWORD:
            return "**" + self.parameter.name
        return self.parameter.name

    @property
    def value(self) -> typing.Any:
        """Parameter value to log.

        :return: If function is bound to class -> value is class instance else default value.
        :rtype: typing.Any
        """
        return self._value

    @property
    def annotation(self) -> typing.Union[inspect.Parameter.empty, str]:
        """Parameter annotation.

        :return: parameter annotation from signature
        :rtype: typing.Union[inspect.Parameter.empty, str]
        """
        return self.parameter.annotation

    @property
    def kind(self) -> int:
        """Parameter kind.

        :return: parameter kind from inspect.Parameter
        :rtype: int
        """
        # noinspection PyTypeChecker
        return self.parameter.kind  # type: ignore

    # noinspection PyTypeChecker
    def __hash__(self) -> typing.NoReturn:
        """Block hashing.

        :raises TypeError: Not hashable.
        """
        msg = f"unhashable type: '{self.__class__.__name__}'"
        raise TypeError(msg)

    def __repr__(self) -> str:
        """Debug purposes.

        :return: parameter repr for debug purposes
        :rtype: str
        """
        return f'<{self.__class__.__name__} "{self}">'


def _prepare_repr(func: typing.Union[types.FunctionType, types.MethodType]) -> typing.List[ReprParameter]:
    """Get arguments lists with defaults.

    :param func: Callable object to process
    :type func: typing.Union[types.FunctionType, types.MethodType]
    :return: repr of callable parameter from signature
    :rtype: typing.List[ReprParameter]
    """
    ismethod: bool = isinstance(func, types.MethodType)
    self_processed: bool = False
    result: typing.List[ReprParameter] = []
    if not ismethod:
        real_func: typing.Callable[..., typing.Any] = func
    else:
        real_func = func.__func__  # type: ignore

    for param in inspect.signature(real_func).parameters.values():
        if not self_processed and ismethod and func.__self__ is not None:  # type: ignore
            result.append(ReprParameter(param, value=func.__self__))  # type: ignore
            self_processed = True
        else:
            result.append(ReprParameter(param))

    return result


class PrettyFormat(metaclass=abc.ABCMeta):
    """Pretty Formatter.

    Designed for usage as __repr__ and __str__ replacement on complex objects
    """

    __slots__ = ("__max_indent", "__indent_step")

    def __init__(self, max_indent: int = 20, indent_step: int = 4) -> None:
        """Pretty Formatter.

        :param max_indent: maximal indent before classic repr() call
        :type max_indent: int
        :param indent_step: step for the next indentation level
        :type indent_step: int
        """
        self.__max_indent: int = max_indent
        self.__indent_step: int = indent_step

    @property
    def max_indent(self) -> int:
        """Max indent getter.

        :return: maximal indent before switch to normal repr
        :rtype: int
        """
        return self.__max_indent

    @property
    def indent_step(self) -> int:
        """Indent step getter.

        :return: indent step for nested definitions
        :rtype: int
        """
        return self.__indent_step

    def next_indent(self, indent: int, multiplier: int = 1) -> int:
        """Next indentation value.

        :param indent: current indentation value
        :type indent: int
        :param multiplier: step multiplier
        :type multiplier: int
        :return: next indentation value
        :rtype: int
        """
        return indent + multiplier * self.indent_step

    def _repr_callable(self, src: typing.Union[types.FunctionType, types.MethodType], indent: int = 0) -> str:
        """Repr callable object (function or method).

        :param src: Callable to process
        :type src: typing.Union[types.FunctionType, types.MethodType]
        :param indent: start indentation
        :type indent: int
        :return: Repr of function or method with signature.
        :rtype: str
        """
        param_str: str = ""
        prefix: str = "\n" + " " * self.next_indent(indent)

        for param in _prepare_repr(src):
            param_str += f"{prefix}{param.name}"
            if param.annotation is not param.empty:
                param_str += f": {getattr(param.annotation, '__name__', param.annotation)!s}"
            if param.value is not param.empty:
                param_str += f"={self.process_element(src=param.value, indent=indent, no_indent_start=True)}"
            param_str += ","

        if param_str:
            param_str += "\n" + " " * indent

        sig: inspect.Signature = inspect.signature(src)
        if sig.return_annotation is inspect.Parameter.empty:
            annotation: str = ""
        else:
            annotation = f" -> {getattr(sig.return_annotation, '__name__', sig.return_annotation)!s}"

        return (
            f"{'':<{indent}}"
            f"<{src.__class__.__name__} {src.__module__}.{src.__name__} with interface ({param_str}){annotation}>"
        )

    @abc.abstractmethod
    def _repr_simple(self, src: typing.Any, indent: int = 0, no_indent_start: bool = False) -> str:
        """Repr object without iteration.

        :param src: Source object
        :type src: typing.Any
        :param indent: start indentation
        :type indent: int
        :param no_indent_start: ignore indent
        :type no_indent_start: bool
        :return: simple repr() over object
        :rtype: str
        """

    @abc.abstractmethod
    def _repr_dict_items(self, src: typing.Dict[typing.Any, typing.Any], indent: int = 0) -> str:
        """Repr dict items.

        :param src: object to process
        :type src: typing.Dict
        :param indent: start indentation
        :type indent: int
        :return: repr of key/value pairs from dict
        :rtype: str
        """

    @staticmethod
    @abc.abstractmethod
    def _repr_iterable_item(
        obj_type: str, prefix: str, indent: int, no_indent_start: bool, result: str, suffix: str
    ) -> str:
        """Repr iterable item.

        :param obj_type: Object type
        :type obj_type: str
        :param prefix: prefix
        :type prefix: str
        :param indent: start indentation
        :type indent: int
        :param no_indent_start: do not indent open bracket and simple parameters
        :type no_indent_start: bool
        :param result: result of pre-formatting
        :type result: str
        :param suffix: suffix
        :type suffix: str
        :return: formatted repr of "result" with prefix and suffix to explain type.
        :rtype: str
        """

    def _repr_iterable_items(self, src: typing.Iterable[typing.Any], indent: int = 0) -> str:
        """Repr iterable items (not designed for dicts).

        :param src: object to process
        :type src: typing.Iterable
        :param indent: start indentation
        :type indent: int
        :return: repr of elements in iterable item
        :rtype: str
        """
        next_indent: int = self.next_indent(indent)
        buf: typing.List[str] = []
        for elem in src:
            buf.append("\n")
            buf.append(self.process_element(src=elem, indent=next_indent))
            buf.append(",")
        return "".join(buf)

    @property
    @abc.abstractmethod
    def _magic_method_name(self) -> str:
        """Magic method name.

        :return: magic method name to lookup in processing objects
        :rtype: str
        """

    def process_element(self, src: typing.Any, indent: int = 0, no_indent_start: bool = False) -> str:
        """Make human readable representation of object.

        :param src: object to process
        :type src: typing.Any
        :param indent: start indentation
        :type indent: int
        :param no_indent_start: do not indent open bracket and simple parameters
        :type no_indent_start: bool
        :return: formatted string
        :rtype: str
        """
        if hasattr(src, self._magic_method_name):
            result = getattr(src, self._magic_method_name)(self, indent=indent, no_indent_start=no_indent_start)
            return result  # type: ignore

        if _known_callable(src):
            return self._repr_callable(src=src, indent=indent)

        if _simple(src) or indent >= self.max_indent or not src:
            return self._repr_simple(src=src, indent=indent, no_indent_start=no_indent_start)

        if isinstance(src, dict):
            prefix, suffix = "{", "}"
            result = self._repr_dict_items(src=src, indent=indent)
        else:
            if isinstance(src, list):
                prefix, suffix = "[", "]"
            elif isinstance(src, tuple):
                prefix, suffix = "(", ")"
            else:
                prefix, suffix = "{", "}"
            result = self._repr_iterable_items(src=src, indent=indent)
        if type(src) in (list, tuple, set, dict):  # pylint: disable=unidiomatic-typecheck
            return f"{'':<{indent if not no_indent_start else 0}}{prefix}{result}\n{'':<{indent}}{suffix}"
        return self._repr_iterable_item(
            obj_type=src.__class__.__name__,
            prefix=prefix,
            indent=indent,
            no_indent_start=no_indent_start,
            result=result,
            suffix=suffix,
        )

    def __call__(self, src: typing.Any, indent: int = 0, no_indent_start: bool = False) -> str:
        """Make human readable representation of object. The main entry point.

        :param src: object to process
        :type src: typing.Any
        :param indent: start indentation
        :type indent: int
        :param no_indent_start: do not indent open bracket and simple parameters
        :type no_indent_start: bool
        :return: formatted string
        :rtype: str
        """
        result = self.process_element(src, indent=indent, no_indent_start=no_indent_start)
        return result


class PrettyRepr(PrettyFormat):
    """Pretty repr.

    Designed for usage as __repr__ replacement on complex objects
    """

    __slots__ = ()

    @property
    def _magic_method_name(self) -> str:
        """Magic method name.

        :return: magic method name to lookup in processing objects
        :rtype: str
        """
        return "__pretty_repr__"

    def _repr_simple(self, src: typing.Any, indent: int = 0, no_indent_start: bool = False) -> str:
        """Repr object without iteration.

        :param src: Source object
        :type src: typing.Any
        :param indent: start indentation
        :type indent: int
        :param no_indent_start: ignore indent
        :type no_indent_start: bool
        :return: simple repr() over object, except strings (add prefix) and set (uniform py2/py3)
        :rtype: str
        """
        return f"{'':<{0 if no_indent_start else indent}}{src!r}"

    def _repr_dict_items(self, src: typing.Dict[typing.Any, typing.Any], indent: int = 0) -> str:
        """Repr dict items.

        :param src: object to process
        :type src: typing.Dict
        :param indent: start indentation
        :type indent: int
        :return: repr of key/value pairs from dict
        :rtype: str
        """
        max_len: int = max((len(repr(key)) for key in src)) if src else 0
        next_indent: int = self.next_indent(indent)
        prefix: str = "\n" + " " * next_indent
        buf: typing.List[str] = []
        for key, val in src.items():
            buf.append(prefix)
            buf.append(f"{key!r:{max_len}}: ")
            buf.append(self.process_element(val, indent=next_indent, no_indent_start=True))
            buf.append(",")
        return "".join(buf)

    @staticmethod
    def _repr_iterable_item(
        obj_type: str, prefix: str, indent: int, no_indent_start: bool, result: str, suffix: str
    ) -> str:
        """Repr iterable item.

        :param obj_type: Object type
        :type obj_type: str
        :param prefix: prefix
        :type prefix: str
        :param indent: start indentation
        :type indent: int
        :param no_indent_start: do not indent open bracket and simple parameters
        :type no_indent_start: bool
        :param result: result of pre-formatting
        :type result: str
        :param suffix: suffix
        :type suffix: str
        :return: formatted repr of "result" with prefix and suffix to explain type.
        :rtype: str
        """
        return f"{'':<{indent if not no_indent_start else 0}}{obj_type}({prefix}{result}\n{'':<{indent}}{suffix})"


class PrettyStr(PrettyFormat):
    """Pretty str.

    Designed for usage as __str__ replacement on complex objects
    """

    __slots__ = ()

    @property
    def _magic_method_name(self) -> str:
        """Magic method name.

        :rtype: str
        """
        return "__pretty_str__"

    @staticmethod
    def _strings_str(indent: int, val: typing.Union[bytes, str]) -> str:
        """Custom str for strings and binary strings.

        :param indent: result indent
        :type indent: int
        :param val: value for repr
        :type val: typing.Union[bytes, str]
        :return: indented string as `str`
        :rtype: str
        """
        if isinstance(val, bytes):
            string: str = val.decode(encoding="utf-8", errors="backslashreplace")
        else:
            string = val
        return f"{'':<{indent}}{string}"

    def _repr_simple(self, src: typing.Any, indent: int = 0, no_indent_start: bool = False) -> str:
        """Repr object without iteration.

        :param src: Source object
        :type src: typing.Any
        :param indent: start indentation
        :type indent: int
        :param no_indent_start: ignore indent
        :type no_indent_start: bool
        :return: simple repr() over object, except strings (decode) and set (uniform py2/py3)
        :rtype: str
        """
        indent = 0 if no_indent_start else indent
        if isinstance(src, (bytes, str)):
            return self._strings_str(indent=indent, val=src)
        return f"{'':<{indent}}{src!s}"

    def _repr_dict_items(self, src: typing.Dict[typing.Any, typing.Any], indent: int = 0) -> str:
        """Repr dict items.

        :param src: object to process
        :type src: typing.Dict
        :param indent: start indentation
        :type indent: int
        :return: repr of key/value pairs from dict
        :rtype: str
        """
        max_len = max((len(str(key)) for key in src)) if src else 0
        next_indent: int = self.next_indent(indent)
        prefix: str = "\n" + " " * next_indent
        buf: typing.List[str] = []
        for key, val in src.items():
            buf.append(prefix)
            buf.append(f"{key!s:{max_len}}: ")
            buf.append(self.process_element(val, indent=next_indent, no_indent_start=True))
            buf.append(",")
        return "".join(buf)

    @staticmethod
    def _repr_iterable_item(
        obj_type: str, prefix: str, indent: int, no_indent_start: bool, result: str, suffix: str
    ) -> str:
        """Repr iterable item.

        :param obj_type: Object type
        :type obj_type: str
        :param prefix: prefix
        :type prefix: str
        :param indent: start indentation
        :type indent: int
        :param no_indent_start: do not indent open bracket and simple parameters
        :type no_indent_start: bool
        :param result: result of pre-formatting
        :type result: str
        :param suffix: suffix
        :type suffix: str
        :return: formatted repr of "result" with prefix and suffix to explain type.
        :rtype: str
        """
        return f"{'':<{indent if not no_indent_start else 0}}{prefix}{result}\n{'':<{indent}}{suffix}"


def pretty_repr(
    src: typing.Any, indent: int = 0, no_indent_start: bool = False, max_indent: int = 20, indent_step: int = 4
) -> str:
    """Make human readable repr of object.

    :param src: object to process
    :type src: typing.Any
    :param indent: start indentation, all next levels is +indent_step
    :type indent: int
    :param no_indent_start: do not indent open bracket and simple parameters
    :type no_indent_start: bool
    :param max_indent: maximal indent before classic repr() call
    :type max_indent: int
    :param indent_step: step for the next indentation level
    :type indent_step: int
    :return: formatted string
    :rtype: str
    """
    return PrettyRepr(max_indent=max_indent, indent_step=indent_step)(
        src=src, indent=indent, no_indent_start=no_indent_start
    )


def pretty_str(
    src: typing.Any, indent: int = 0, no_indent_start: bool = False, max_indent: int = 20, indent_step: int = 4
) -> str:
    """Make human readable str of object.

    :param src: object to process
    :type src: typing.Any
    :param indent: start indentation, all next levels is +indent_step
    :type indent: int
    :param no_indent_start: do not indent open bracket and simple parameters
    :type no_indent_start: bool
    :param max_indent: maximal indent before classic repr() call
    :type max_indent: int
    :param indent_step: step for the next indentation level
    :type indent_step: int
    :return: formatted string
    """
    return PrettyStr(max_indent=max_indent, indent_step=indent_step)(
        src=src, indent=indent, no_indent_start=no_indent_start
    )
