#    Copyright 2016 - 2022 Alexey Stepanov aka penguinolog

#    Copyright 2016 Mirantis, Inc.

#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at

#         http://www.apache.org/licenses/LICENSE-2.0

#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""repr_utils module.

This is no reason to import this submodule directly, all required methods is
available from the main module.
"""

from __future__ import annotations

import abc
import collections
import types
from inspect import Parameter
from inspect import Signature
from inspect import signature
from typing import TYPE_CHECKING
from typing import Any
from typing import ForwardRef
from typing import NoReturn
from typing import Protocol
from typing import get_type_hints
from typing import runtime_checkable

if TYPE_CHECKING:
    import dataclasses
    from collections.abc import Callable
    from collections.abc import Iterable

    from rich.repr import Result as RichReprResult


__all__ = ("PrettyFormat", "PrettyRepr", "PrettyStr", "pretty_repr", "pretty_str")

_SIMPLE_MAGIC_ATTRIBUTES = ("__repr__", "__str__")


@runtime_checkable
class _AttributeHolderProto(Protocol):
    __slots__ = ()

    def _get_kwargs(self) -> list[tuple[str, Any]]:
        """Protocol stub."""

    def _get_args(self) -> list[str]:
        """Protocol stub."""


@runtime_checkable
class _NamedTupleProto(Protocol):
    __slots__ = ()

    def _asdict(self) -> dict[str, Any]:
        """Protocol stub."""

    def __getnewargs__(self) -> tuple[Any, ...]:
        """Protocol stub."""

    def _replace(self, /, **kwds: dict[str, Any]) -> _NamedTupleProto:
        """Protocol stub."""

    @classmethod
    def _make(cls, iterable: Iterable[Any]) -> _NamedTupleProto:
        """Protocol stub."""


@runtime_checkable
class _DataClassProto(Protocol):
    __slots__ = ()

    __dataclass_params__: dataclasses._DataclassParams  # type: ignore[name-defined]
    __dataclass_fields__: dict[str, dataclasses.Field[Any]] = {}  # noqa: RUF012


@runtime_checkable
class _RichReprProto(Protocol):
    """Protocol for type checking."""

    def __rich_repr__(self) -> RichReprResult:  # noqa: PLW3201,RUF100
        """Protocol stub."""


def _known_callable(item: Any) -> bool:
    """Check for possibility to parse callable.

    :param item:  item to check for repr() way
    :type item: Any
    :return: item is callable and should be processed not using repr
    :rtype: bool
    """
    return isinstance(item, (types.FunctionType, types.MethodType))


def _simple(item: Any) -> bool:
    """Check for nested iterations: True, if not.

    :param item: item to check for repr() way
    :type item: Any
    :return: use repr() iver item by default
    :rtype: bool
    """
    return not any(
        (
            isinstance(item, data_type)
            and all(
                getattr(type(item), attribute) is getattr(data_type, attribute)
                for attribute in _SIMPLE_MAGIC_ATTRIBUTES
            )
        )
        for data_type in (list, set, tuple, dict, frozenset, collections.deque)
    )


class ReprParameter:
    """Parameter wrapper wor repr and str operations over signature."""

    __slots__ = ("_parameter", "_value")

    POSITIONAL_ONLY = Parameter.POSITIONAL_ONLY
    POSITIONAL_OR_KEYWORD = Parameter.POSITIONAL_OR_KEYWORD
    VAR_POSITIONAL = Parameter.VAR_POSITIONAL
    KEYWORD_ONLY = Parameter.KEYWORD_ONLY
    VAR_KEYWORD = Parameter.VAR_KEYWORD

    empty = Parameter.empty

    def __init__(self, parameter: Parameter, value: Any = Parameter.empty) -> None:
        """Parameter-like object store for repr and str tasks.

        :param parameter: parameter from signature
        :type parameter: Parameter
        :param value: default value override
        :type value: Any
        """
        self._parameter: Parameter = parameter
        self._value: Any = value if value is not parameter.empty else parameter.default

    @property
    def parameter(self) -> Parameter:
        """Parameter object.

        :return: original Parameter object
        :rtype: Parameter
        """
        return self._parameter

    @property
    def name(self) -> None | str:
        """Parameter name.

        :return: parameter name. For `*args` and `**kwargs` add corresponding prefixes
        :rtype: None | str
        """
        if self.kind == Parameter.VAR_POSITIONAL:
            return "*" + self.parameter.name
        if self.kind == Parameter.VAR_KEYWORD:
            return "**" + self.parameter.name
        return self.parameter.name

    @property
    def value(self) -> Any:
        """Parameter value to log.

        :return: If function is bound to class -> value is class instance else default value.
        :rtype: Any
        """
        return self._value

    @property
    def annotation(self) -> Parameter.empty | str:  # type: ignore[valid-type]
        """Parameter annotation.

        :return: parameter annotation from signature
        :rtype: Parameter.empty | str
        """
        return self.parameter.annotation  # type: ignore[no-any-return]

    @property
    def kind(self) -> int:
        """Parameter kind.

        :return: parameter kind from Parameter
        :rtype: int
        """
        # noinspection PyTypeChecker
        return self.parameter.kind

    def __hash__(self) -> NoReturn:  # pylint: disable=invalid-hash-returned
        """Block hashing.

        :raises TypeError: Not hashable.
        """
        msg = f"not hashable type: '{self.__class__.__name__}'"
        raise TypeError(msg)

    def __repr__(self) -> str:
        """Debug purposes.

        :return: parameter repr for debug purposes
        :rtype: str
        """
        return f'<{self.__class__.__name__} "{self}">'


def _prepare_repr(func: types.FunctionType | types.MethodType) -> list[ReprParameter]:
    """Get arguments lists with defaults.

    :param func: Callable object to process
    :type func: types.FunctionType | types.MethodType
    :return: repr of callable parameter from signature
    :rtype: list[ReprParameter]
    """
    ismethod: bool = isinstance(func, types.MethodType)
    self_processed: bool = False
    result: list[ReprParameter] = []
    if not ismethod:
        real_func: Callable[..., Any] = func
    else:
        real_func = func.__func__  # type: ignore[union-attr]

    for param in signature(real_func).parameters.values():
        if not self_processed and ismethod and func.__self__ is not None:  # type: ignore[union-attr]
            result.append(ReprParameter(param, value=func.__self__))  # type: ignore[union-attr]
            self_processed = True
        else:
            result.append(ReprParameter(param))

    return result


class PrettyFormat(abc.ABC):
    """Pretty Formatter.

    Designed for usage as __repr__ and __str__ replacement on complex objects
    """

    __slots__ = ("__indent_step", "__max_indent", "__max_iter")

    def __init__(self, max_indent: int = 20, max_iter: int = 0, indent_step: int = 4) -> None:
        """Pretty Formatter.

        :param max_indent: maximal indent before classic repr() call
        :type max_indent: int
        :param indent_step: step for the next indentation level
        :type indent_step: int
        """
        self.__max_indent: int = max_indent
        self.__max_iter: int = max_iter
        self.__indent_step: int = indent_step

    @property
    def max_indent(self) -> int:
        """Max indent getter.

        :return: maximal indent before switch to normal repr
        :rtype: int
        """
        return self.__max_indent

    @property
    def max_iter(self) -> int:
        """Max iterable items getter.

        :return: maximal items count for iterable objects
        :rtype: int
        """
        return self.__max_iter

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

    def _repr_callable(
        self,
        src: types.FunctionType | types.MethodType,
        indent: int = 0,
    ) -> str:
        """Repr callable object (function or method).

        :param src: Callable to process
        :type src: types.FunctionType | types.MethodType
        :param indent: start indentation
        :type indent: int
        :return: Repr of function or method with signature.
        :rtype: str
        """
        param_repr: list[str] = []

        next_indent = self.next_indent(indent)
        prefix: str = "\n" + " " * next_indent

        for param in _prepare_repr(src):
            param_repr.append(f"{prefix}{param.name}")
            annotation_exist = param.annotation is not param.empty  # type: ignore[comparison-overlap]
            if annotation_exist:
                param_repr.append(f": {getattr(param.annotation, '__name__', param.annotation)!s}")
            if param.value is not param.empty:
                if annotation_exist:
                    param_repr.append(" = ")
                else:
                    param_repr.append("=")
                param_repr.append(self.process_element(src=param.value, indent=next_indent, no_indent_start=True))
            param_repr.append(",")

        if param_repr:
            param_repr.extend(("\n", " " * indent))

        param_str = "".join(param_repr)

        sig: Signature = signature(src)
        if sig.return_annotation is Parameter.empty:
            annotation: str = ""
        elif sig.return_annotation is type(None):
            # Python 3.10 special case
            annotation = " -> None"
        else:
            annotation = f" -> {getattr(sig.return_annotation, '__name__', sig.return_annotation)!s}"

        return (
            f"{'':<{indent}}"
            f"<{src.__class__.__name__} {src.__module__}.{src.__name__} with interface ({param_str}){annotation}>"
        )

    def _repr_attribute_holder(
        self,
        src: _AttributeHolderProto,
        indent: int = 0,
        no_indent_start: bool = False,
    ) -> str:
        """Repr attribute holder object (like argparse objects).

        :param src: attribute holder object to process
        :type src: _AttributeHolderProto
        :param indent: start indentation
        :type indent: int
        :param no_indent_start: do not indent open bracket and simple parameters
        :type no_indent_start: bool
        :return: Repr of attribute holder object.
        :rtype: str
        """
        param_repr: list[str] = []
        star_args: dict[str, Any] = {}

        next_indent = self.next_indent(indent)
        prefix: str = "\n" + " " * next_indent

        for arg in src._get_args():  # pylint: disable=protected-access
            repr_val = self.process_element(arg, indent=next_indent)
            param_repr.append(f"{prefix}{repr_val},")

        for name, value in src._get_kwargs():  # pylint: disable=protected-access
            if name.isidentifier():
                repr_val = self.process_element(value, indent=next_indent, no_indent_start=True)
                param_repr.append(f"{prefix}{name}={repr_val},")
            else:
                star_args[name] = value

        if star_args:
            repr_val = self.process_element(star_args, indent=next_indent, no_indent_start=True)
            param_repr.append(f"{prefix}**{repr_val},")

        if param_repr:
            param_repr.extend(("\n", " " * indent))

        param_str = "".join(param_repr)
        return f"{'':<{indent if not no_indent_start else 0}}{src.__module__}.{src.__class__.__name__}({param_str})"

    def _repr_named_tuple(
        self,
        src: _NamedTupleProto,
        indent: int = 0,
        no_indent_start: bool = False,
    ) -> str:
        """Repr named tuple.

        :param src: named tuple object to process
        :type src: _NamedTupleProto
        :param indent: start indentation
        :type indent: int
        :param no_indent_start: do not indent open bracket and simple parameters
        :type no_indent_start: bool
        :return: Repr of named tuple object.
        :rtype: str
        """
        param_repr: list[str] = []

        # noinspection PyBroadException
        try:
            args_annotations: dict[str, Any] = get_type_hints(type(src))
        except BaseException:  # NOSONAR
            args_annotations = {}

        next_indent = self.next_indent(indent)
        prefix: str = "\n" + " " * next_indent

        for arg_name, value in src._asdict().items():
            repr_val = self.process_element(value, indent=next_indent, no_indent_start=True)
            param_repr.append(f"{prefix}{arg_name}={repr_val},")
            if arg_name in args_annotations and not isinstance(getattr(args_annotations, arg_name, None), ForwardRef):
                annotation = getattr(args_annotations[arg_name], "__name__", args_annotations[arg_name])
                param_repr.append(f"  # type: {annotation!s}")

        if param_repr:
            param_repr.extend(("\n", " " * indent))

        param_str = "".join(param_repr)
        return f"{'':<{indent if not no_indent_start else 0}}{src.__module__}.{src.__class__.__name__}({param_str})"

    def _repr_dataclass(
        self,
        src: _DataClassProto,
        indent: int = 0,
        no_indent_start: bool = False,
    ) -> str:
        """Repr dataclass.

        :param src: dataclass object to process
        :type src: _DataClassProto
        :param indent: start indentation
        :type indent: int
        :param no_indent_start: do not indent open bracket and simple parameters
        :type no_indent_start: bool
        :return: Repr of dataclass.
        :rtype: str
        """
        param_repr: list[str] = []

        next_indent = self.next_indent(indent)
        prefix: str = "\n" + " " * next_indent

        for arg_name, field in src.__dataclass_fields__.items():
            if not field.repr:
                continue
            repr_val = self.process_element(getattr(src, arg_name), indent=next_indent, no_indent_start=True)

            comment: list[str] = []

            if field.type:
                if isinstance(field.type, str):
                    comment.append(f"type: {field.type}")
                else:
                    comment.append(f"type: {field.type.__name__}")
            if getattr(field, "kw_only", False):  # python 3.10+
                comment.append("kw_only")

            if comment:
                comment_str = "  # " + "  # ".join(comment)
            else:
                comment_str = ""

            param_repr.append(f"{prefix}{arg_name}={repr_val},{comment_str}")

        if param_repr:
            param_repr.extend(("\n", " " * indent))

        param_str = "".join(param_repr)
        return f"{'':<{indent if not no_indent_start else 0}}{src.__module__}.{src.__class__.__name__}({param_str})"

    @abc.abstractmethod
    def _repr_simple(
        self,
        src: Any,
        indent: int = 0,
        no_indent_start: bool = False,
    ) -> str:
        """Repr object without iteration.

        :param src: Source object
        :type src: Any
        :param indent: start indentation
        :type indent: int
        :param no_indent_start: ignore indent
        :type no_indent_start: bool
        :return: simple repr() over object
        :rtype: str
        """

    @abc.abstractmethod
    def _repr_dict_items(
        self,
        src: dict[Any, Any],
        indent: int = 0,
    ) -> str:
        """Repr dict items.

        :param src: object to process
        :type src: dict[Any, Any]
        :param indent: start indentation
        :type indent: int
        :return: repr of key/value pairs from dict
        :rtype: str
        """

    @staticmethod
    @abc.abstractmethod
    def _repr_iterable_item(
        obj_type: str,
        prefix: str,
        indent: int,
        no_indent_start: bool,
        result: str,
        suffix: str,
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

    def _repr_iterable_items(
        self,
        src: Iterable[Any],
        indent: int = 0,
    ) -> str:
        """Repr iterable items (not designed for dicts).

        :param src: object to process
        :type src: Iterable[Any]
        :param indent: start indentation
        :type indent: int
        :return: repr of elements in iterable item
        :rtype: str
        """
        next_indent: int = self.next_indent(indent)
        buf: list[str] = []

        for idx, elem in enumerate(src, start=1):
            buf.extend(("\n", self.process_element(src=elem, indent=next_indent)))

            if idx == self.max_iter:
                buf.append("...")
                break

            buf.append(",")
        return "".join(buf)

    def _repr_rich(
        self,
        src: _RichReprProto,
        indent: int = 0,
        no_indent_start: bool = False,
    ) -> str:
        """Repr of objects with rich defined repr.

        :param src: object to process
        :type src: Any
        :param indent: start indentation
        :type indent: int
        :param no_indent_start: do not indent open bracket and simple parameters
        :type no_indent_start: bool
        :return: formatted string
        :rtype: str
        """
        param_repr: list[str] = []

        next_indent = self.next_indent(indent)
        prefix: str = "\n" + " " * next_indent

        for arg in src.__rich_repr__():
            if isinstance(arg, tuple):
                if len(arg) == 1:
                    arg_name = None
                    default = ()
                    value = arg[0]
                else:
                    arg_name, value, *default = arg  # type: ignore[assignment]

                repr_val = self.process_element(value, indent=next_indent, no_indent_start=True)

                if arg_name is None:
                    param_repr.append(f"{prefix}{repr_val},")
                else:
                    if default and default[0] == value:
                        # standard behavior for rich
                        continue

                    param_repr.append(f"{prefix}{arg_name}={repr_val},")

            else:
                repr_val = self.process_element(arg, indent=next_indent, no_indent_start=True)
                param_repr.append(f"{prefix}{repr_val},")

        if param_repr:
            param_repr.extend(("\n", " " * indent))

        param_str = "".join(param_repr)
        return f"{'':<{indent if not no_indent_start else 0}}{src.__module__}.{src.__class__.__name__}({param_str})"

    @property
    @abc.abstractmethod
    def _magic_method_name(self) -> str:
        """Magic method name.

        :return: magic method name to lookup in processing objects
        :rtype: str
        """

    def process_element(
        self,
        src: Any,
        indent: int = 0,
        no_indent_start: bool = False,
    ) -> str:
        """Make human readable representation of object.

        :param src: object to process
        :type src: Any
        :param indent: start indentation
        :type indent: int
        :param no_indent_start: do not indent open bracket and simple parameters
        :type no_indent_start: bool
        :return: formatted string
        :rtype: str
        """
        if hasattr(src, self._magic_method_name):
            return getattr(  # type: ignore[no-any-return]
                src,
                self._magic_method_name,
            )(
                self,
                indent=indent,
                no_indent_start=no_indent_start,
            )

        if isinstance(src, _RichReprProto):
            return self._repr_rich(src=src, indent=indent)

        if _known_callable(src):
            return self._repr_callable(src=src, indent=indent)

        if isinstance(src, _AttributeHolderProto):
            return self._repr_attribute_holder(src=src, indent=indent, no_indent_start=no_indent_start)

        if isinstance(src, tuple) and isinstance(src, _NamedTupleProto):
            return self._repr_named_tuple(src=src, indent=indent, no_indent_start=no_indent_start)

        if isinstance(src, _DataClassProto) and not isinstance(src, type) and src.__dataclass_params__.repr:
            return self._repr_dataclass(src=src, indent=indent, no_indent_start=no_indent_start)

        if _simple(src) or indent >= self.max_indent or not src:
            return self._repr_simple(src=src, indent=indent, no_indent_start=no_indent_start)

        if isinstance(src, dict):
            prefix, suffix = "{", "}"
            result = self._repr_dict_items(src=src, indent=indent)
        elif isinstance(src, collections.deque):
            result = self._repr_iterable_items(src=src, indent=self.next_indent(indent))
            prefix, suffix = "(", ")"
        else:
            if isinstance(src, list):
                prefix, suffix = "[", "]"
            elif isinstance(src, tuple):
                prefix, suffix = "(", ")"
            elif isinstance(src, (set, frozenset)):
                prefix, suffix = "{", "}"
            else:
                prefix, suffix = "", ""
            result = self._repr_iterable_items(src=src, indent=indent)

        if isinstance(src, collections.deque):
            next_indent = self.next_indent(indent)
            return (
                f"{'':<{indent if not no_indent_start else 0}}"
                f"{src.__class__.__name__}(\n"
                f"{'':<{next_indent}}{prefix}{result}\n"
                f"{'':<{next_indent}}{suffix},\n"
                f"{'':<{self.next_indent(indent)}}maxlen={src.maxlen},\n"
                f"{'':<{indent}})"
            )

        if type(src) in {list, tuple, set, dict}:
            return f"{'':<{indent if not no_indent_start else 0}}{prefix}{result}\n{'':<{indent}}{suffix}"

        return self._repr_iterable_item(
            obj_type=src.__class__.__name__,
            prefix=prefix,
            indent=indent,
            no_indent_start=no_indent_start,
            result=result,
            suffix=suffix,
        )

    def __call__(
        self,
        src: Any,
        indent: int = 0,
        no_indent_start: bool = False,
    ) -> str:
        """Make human-readable representation of object. The main entry point.

        :param src: object to process
        :type src: Any
        :param indent: start indentation
        :type indent: int
        :param no_indent_start: do not indent open bracket and simple parameters
        :type no_indent_start: bool
        :return: formatted string
        :rtype: str
        """
        return self.process_element(src, indent=indent, no_indent_start=no_indent_start)


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

    def _repr_simple(
        self,
        src: Any,
        indent: int = 0,
        no_indent_start: bool = False,
    ) -> str:
        """Repr object without iteration.

        :param src: Source object
        :type src: Any
        :param indent: start indentation
        :type indent: int
        :param no_indent_start: ignore indent
        :type no_indent_start: bool
        :return: simple repr() over object, except strings (add prefix) and set (uniform py2/py3)
        :rtype: str
        """
        return f"{'':<{0 if no_indent_start else indent}}{src!r}"

    def _repr_dict_items(
        self,
        src: dict[Any, Any],
        indent: int = 0,
    ) -> str:
        """Repr dict items.

        :param src: object to process
        :type src: dict[Any, Any]
        :param indent: start indentation
        :type indent: int
        :return: repr of key/value pairs from dict
        :rtype: str
        """
        max_len: int = max(len(repr(key)) for key in src) if src else 0
        next_indent: int = self.next_indent(indent)
        prefix: str = "\n" + " " * next_indent
        buf: list[str] = []
        for key, val in src.items():
            buf.extend(
                (
                    prefix,
                    f"{key!r:{max_len}}: ",
                    self.process_element(val, indent=next_indent, no_indent_start=True),
                    ",",
                )
            )
        return "".join(buf)

    @staticmethod
    def _repr_iterable_item(
        obj_type: str,
        prefix: str,
        indent: int,
        no_indent_start: bool,
        result: str,
        suffix: str,
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
    def _strings_str(
        indent: int,
        val: bytes | str,
    ) -> str:
        """Custom str for strings and binary strings.

        :param indent: result indent
        :type indent: int
        :param val: value for repr
        :type val: bytes | str
        :return: indented string as `str`
        :rtype: str
        """
        if isinstance(val, bytes):
            string: str = val.decode(encoding="utf-8", errors="backslashreplace")
        else:
            string = val
        return f"{'':<{indent}}{string}"

    def _repr_simple(
        self,
        src: Any,
        indent: int = 0,
        no_indent_start: bool = False,
    ) -> str:
        """Repr object without iteration.

        :param src: Source object
        :type src: Any
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

    def _repr_dict_items(
        self,
        src: dict[Any, Any],
        indent: int = 0,
    ) -> str:
        """Repr dict items.

        :param src: object to process
        :type src: dict[Any, Any]
        :param indent: start indentation
        :type indent: int
        :return: repr of key/value pairs from dict
        :rtype: str
        """
        max_len = max(len(str(key)) for key in src) if src else 0
        next_indent: int = self.next_indent(indent)
        prefix: str = "\n" + " " * next_indent
        buf: list[str] = []
        for key, val in src.items():
            buf.extend(
                (
                    prefix,
                    f"{key!s:{max_len}}: ",
                    self.process_element(val, indent=next_indent, no_indent_start=True),
                    ",",
                )
            )
        return "".join(buf)

    @staticmethod
    def _repr_iterable_item(
        obj_type: str,
        prefix: str,
        indent: int,
        no_indent_start: bool,
        result: str,
        suffix: str,
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
    src: Any,
    indent: int = 0,
    no_indent_start: bool = False,
    max_indent: int = 20,
    max_iter: int = 0,
    indent_step: int = 4,
) -> str:
    """Make human readable repr of object.

    :param src: object to process
    :type src: Any
    :param indent: start indentation, all next levels is +indent_step
    :type indent: int
    :param no_indent_start: do not indent open bracket and simple parameters
    :type no_indent_start: bool
    :param max_indent: maximal indent before classic repr() call
    :type max_indent: int
    :param max_iter: maximal number of items to iterate
    :type max_iter: int
    :param indent_step: step for the next indentation level
    :type indent_step: int
    :return: formatted string
    :rtype: str
    """
    return PrettyRepr(max_indent=max_indent, max_iter=max_iter, indent_step=indent_step)(
        src=src,
        indent=indent,
        no_indent_start=no_indent_start,
    )


def pretty_str(
    src: Any,
    indent: int = 0,
    no_indent_start: bool = False,
    max_indent: int = 20,
    max_iter: int = 0,
    indent_step: int = 4,
) -> str:
    """Make human readable str of object.

    :param src: object to process
    :type src: Any
    :param indent: start indentation, all next levels is +indent_step
    :type indent: int
    :param no_indent_start: do not indent open bracket and simple parameters
    :type no_indent_start: bool
    :param max_indent: maximal indent before classic repr() call
    :type max_indent: int
    :param max_iter: maximal number of items to log in iterables
    :type max_iter: int
    :param indent_step: step for the next indentation level
    :type indent_step: int
    :return: formatted string
    """
    return PrettyStr(max_indent=max_indent, max_iter=max_iter, indent_step=indent_step)(
        src=src,
        indent=indent,
        no_indent_start=no_indent_start,
    )
