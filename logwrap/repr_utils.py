#    Copyright 2016 - 2025 Alexey Stepanov aka penguinolog

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

This is no reason to import this submodule directly; all required methods are available from the main module.
"""

from __future__ import annotations

import abc
import collections
import operator
import sys
import types
import typing
from inspect import Parameter
from inspect import Signature
from inspect import isclass
from inspect import signature
from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar
from typing import ForwardRef
from typing import NoReturn
from typing import Protocol
from typing import get_type_hints
from typing import runtime_checkable

if sys.version_info < (3, 12):  # `__protocol_attrs__` have been available since python 3.12 only
    # noinspection protected-member
    from typing import _get_protocol_attrs
else:
    _get_protocol_attrs = None

if TYPE_CHECKING:
    import dataclasses
    from collections.abc import Iterable
    from collections.abc import Iterator

    from rich.repr import Result as RichReprResult


__all__ = ("PrettyFormat", "PrettyRepr", "PrettyStr", "pretty_repr", "pretty_str")

# Types which are rendered by a plain repr()/str() call: no dispatch lookups are required for them at all.
_LEAF_TYPES: frozenset[type] = frozenset(
    {bool, bytearray, bytes, complex, float, int, str, type(None), type(Ellipsis), type(NotImplemented)}
)
# Iterable types with dedicated rendering. Tuple form is used for isinstance(), set form - for exact type match.
_CONTAINER_TYPES: tuple[type, ...] = (
    list,
    set,
    tuple,
    dict,
    frozenset,
    collections.deque,
    collections.Counter,
)
_EXACT_CONTAINER_TYPES: frozenset[type] = frozenset(_CONTAINER_TYPES)
_CALLABLE_TYPES = (types.FunctionType, types.MethodType)
# Types rendered without the type name prefix.
_PLAIN_RENDERED_TYPES: frozenset[type] = frozenset(
    {list, tuple, set, dict, collections.deque, collections.Counter},
)


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


# noinspection protected-member
@runtime_checkable
class _DataClassProto(Protocol):
    __slots__ = ()

    __dataclass_params__: dataclasses._DataclassParams  # type: ignore[name-defined]
    __dataclass_fields__: dict[str, dataclasses.Field[Any]] = {}  # noqa: RUF012


@runtime_checkable
class _AttrsProto(Protocol):
    __slots__ = ()

    __attrs_attrs__: tuple[Any, ...] = ()


@runtime_checkable
class _RichReprProto(Protocol):
    """Protocol for type checking."""

    def __rich_repr__(self) -> RichReprResult:  # noqa: PLW3201,RUF100
        """Protocol stub."""


def _protocol_probe(proto: type[Any]) -> str:
    """Get a single protocol member name usable as an inexpensive pre-check before `isinstance()`.

    `isinstance()` over a `runtime_checkable` Protocol costs an `inspect.getattr_static()` call per member,
    while a missing probe attribute already proves that the object does not match the protocol.
    The name is taken from the protocol itself, so the protocols stay the single source of truth:
    there is nothing to keep in sync on protocol change.

    :param proto: Runtime-checkable protocol
    :returns: name of one of the protocol members
    """
    if sys.version_info >= (3, 12):
        members: Iterable[str] = proto.__protocol_attrs__
    else:
        members = _get_protocol_attrs(proto)
    return min(members)


_ATTRIBUTE_HOLDER_PROBE: str = _protocol_probe(_AttributeHolderProto)
_NAMED_TUPLE_PROBE: str = _protocol_probe(_NamedTupleProto)
_DATA_CLASS_PROBE: str = _protocol_probe(_DataClassProto)
_ATTRS_PROBE: str = _protocol_probe(_AttrsProto)
_RICH_REPR_PROBE: str = _protocol_probe(_RichReprProto)


def _simple(item: Any) -> bool:
    """Check for nested iterations: True, if not.

    :param item: Item to check for repr() way
    :return: use repr() over item by default
    """
    item_type: type = type(item)
    if item_type in _EXACT_CONTAINER_TYPES:
        return False
    if not isinstance(item, _CONTAINER_TYPES):
        # Single isinstance() call over all known containers instead of one call per container type.
        return True
    # Container subclass: it is rendered as a container only if it does not define own repr()/str().
    return not any(
        isinstance(item, data_type)
        and item_type.__repr__ is data_type.__repr__
        and item_type.__str__ is data_type.__str__
        for data_type in _CONTAINER_TYPES
    )


def _field_comment(field_type: Any, *, kw_only: bool) -> str:
    """Build trailing comment for a dataclass/attrs field.

    :param field_type: The type of the field as it is stored by dataclasses/attrs
    :param kw_only: field is a keyword-only
    :returns: comment string (empty, if nothing to report)
    """
    if not field_type:
        return "  # kw_only" if kw_only else ""

    if isinstance(field_type, str):
        type_comment = f"type: {field_type}"
    elif isinstance(field_type, ForwardRef):
        type_comment = f"type: {field_type!r}"
    elif isclass(field_type):
        type_comment = f"type: {field_type.__name__}"
    else:
        type_comment = f"type: {field_type!r}"

    if kw_only:
        return f"  # {type_comment}  # kw_only"
    return f"  # {type_comment}"


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

        :param parameter: Parameter from signature
        :param value: default value override
        """
        self._parameter: Parameter = parameter
        self._value: Any = value if value is not parameter.empty else parameter.default

    @property
    def parameter(self) -> Parameter:
        """Parameter object.

        :returns: Original Parameter object
        """
        return self._parameter

    @property
    def name(self) -> str | None:
        """Parameter name.

        :returns: Parameter name. For `*args` and `**kwargs` add corresponding prefixes
        """
        if self.kind == Parameter.VAR_POSITIONAL:
            return "*" + self.parameter.name
        if self.kind == Parameter.VAR_KEYWORD:
            return "**" + self.parameter.name
        return self.parameter.name

    @property
    def value(self) -> Any:
        """Parameter value to log.

        :returns: If a function is bound to class -> value is a class instance else default value.
        """
        return self._value

    @property
    def annotation(self) -> Parameter.empty | str:  # type: ignore[valid-type]
        """Parameter annotation.

        :returns: Parameter annotation from signature
        """
        return self.parameter.annotation  # type: ignore[no-any-return]

    @property
    def kind(self) -> int:
        """Parameter kind.

        :returns: Parameter kind from Parameter
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

        :returns: Parameter repr for debug purposes
        """
        return f'<{self.__class__.__name__} "{self}">'


def _prepare_repr(
    func: types.FunctionType | types.MethodType,
    sig: Signature,
) -> Iterator[ReprParameter]:
    """Get argument lists with defaults.

    :param func: Callable object to process
    :param sig: signature of the unbound callable (calculated by the caller to not do it twice)
    :returns: repr of callable parameter from signature
    """
    params: Iterator[Parameter] = iter(sig.parameters.values())

    if isinstance(func, types.MethodType) and func.__self__ is not None:
        first: Parameter | None = next(params, None)
        if first is not None:
            yield ReprParameter(first, value=func.__self__)

    for param in params:
        yield ReprParameter(param)


class PrettyFormat(abc.ABC):
    """Pretty Formatter.

    Designed for usage as __repr__ and __str__ replacement on complex objects
    """

    __slots__ = ("_indent_step", "_max_indent", "_max_iter")

    # magic method name to lookup in processing objects. Defined by the concrete subclasses.
    _magic_method_name: ClassVar[str]  # pylint: disable=declare-non-slot

    def __init__(
        self,
        max_indent: int = 20,
        max_iter: int = 0,
        indent_step: int = 4,
    ) -> None:
        """Pretty Formatter.

        :param max_indent: Maximal indent before a classic repr() call
        :param indent_step: step for the next indentation level
        """
        self._max_indent: int = max_indent
        self._max_iter: int = max_iter
        self._indent_step: int = indent_step

    @property
    def max_indent(self) -> int:
        """Max indent getter.

        :returns: Maximal indent before switch to normal repr
        """
        return self._max_indent

    @property
    def max_iter(self) -> int:
        """Max iterable items getter.

        :returns: Maximal items count for iterable objects
        """
        return self._max_iter

    @property
    def indent_step(self) -> int:
        """Indent step getter.

        :returns: indent step for nested definitions
        """
        return self._indent_step

    def next_indent(self, indent: int, multiplier: int = 1) -> int:
        """Next indentation value.

        :param indent: Current indentation value
        :param multiplier: step multiplier
        :returns: next indentation value
        """
        return indent + multiplier * self.indent_step

    def _repr_callable(
        self,
        src: types.FunctionType | types.MethodType,
        indent: int = 0,
    ) -> str:
        """Repr callable object (function or method).

        :param src: Callable to process
        :param indent: start indentation
        :returns: Repr of function or method with signature.
        """
        param_repr: list[str] = []

        next_indent: int = indent + self._indent_step
        prefix: str = "\n" + " " * next_indent

        real_func: Any = src.__func__ if isinstance(src, types.MethodType) else src
        sig: Signature = signature(real_func)

        for param in _prepare_repr(src, sig):
            param_repr.extend((prefix, param.name or ""))
            annotation_exist = param.annotation is not Parameter.empty  # type: ignore[comparison-overlap]
            if annotation_exist:
                # noinspection string-conversion-without-dunder-method
                param_repr.append(f": {getattr(param.annotation, '__name__', param.annotation)!s}")
            value = param.value
            if value is not Parameter.empty:
                param_repr.extend(
                    (
                        " = " if annotation_exist else "=",
                        self.process_element(src=value, indent=next_indent, no_indent_start=True),
                    )
                )

            param_repr.append(",")

        if param_repr:
            param_repr.extend(("\n", " " * indent))

        param_str = "".join(param_repr)

        if sig.return_annotation is Parameter.empty:
            annotation: str = ""
        else:
            annotation = f" -> {getattr(sig.return_annotation, '__name__', sig.return_annotation)!s}"

        return (
            f"{' ' * indent}"
            f"<{src.__class__.__name__} {src.__module__}.{src.__name__} with interface ({param_str}){annotation}>"
        )

    def _repr_attribute_holder(
        self,
        src: _AttributeHolderProto,
        indent: int = 0,
        no_indent_start: bool = False,
    ) -> str:
        """Repr attribute holder object (like argparse objects).

        :param src: Attribute holder object to process
        :param indent: start indentation
        :param no_indent_start: do not indent open bracket and simple parameters
        :returns: Repr of an attribute holder object.
        """
        param_repr: list[str] = []
        star_args: dict[str, Any] = {}
        next_indent: int = indent + self._indent_step
        prefix: str = "\n" + " " * next_indent

        # noinspection protected-member
        for arg in src._get_args():  # pylint: disable=protected-access
            param_repr.extend((prefix, self.process_element(arg, indent=next_indent), ","))

        # noinspection protected-member
        for name, value in src._get_kwargs():  # pylint: disable=protected-access
            if name.isidentifier():
                param_repr.extend(
                    (
                        prefix,
                        name,
                        "=",
                        self.process_element(value, indent=next_indent, no_indent_start=True),
                        ",",
                    )
                )
            else:
                star_args[name] = value

        if star_args:
            param_repr.extend(
                (
                    prefix,
                    "**",
                    self.process_element(star_args, indent=next_indent, no_indent_start=True),
                    ",",
                )
            )

        if param_repr:
            param_repr.extend(("\n", " " * indent))

        param_str = "".join(param_repr)
        start: str = "" if no_indent_start else " " * indent
        return f"{start}{src.__module__}.{src.__class__.__name__}({param_str})"

    def _repr_named_tuple(
        self,
        src: _NamedTupleProto,
        indent: int = 0,
        no_indent_start: bool = False,
    ) -> str:
        """Make a repr of namedtuple object.

        :param src: namedtuple object to process
        :param indent: start indentation
        :param no_indent_start: do not indent open bracket and simple parameters
        :returns: Repr of a namedtuple object.
        """
        param_repr: list[str] = []

        # noinspection PyBroadException
        try:
            args_annotations: dict[str, Any] = get_type_hints(type(src))
        except BaseException:  # NOQA:BLE001  # It's a goal
            args_annotations = {}

        next_indent: int = indent + self._indent_step
        prefix: str = "\n" + " " * next_indent

        # noinspection protected-member
        for arg_name, value in src._asdict().items():
            param_repr.extend(
                (
                    prefix,
                    arg_name,
                    "=",
                    self.process_element(
                        value,
                        indent=next_indent,
                        no_indent_start=True,
                    ),
                    ",",
                )
            )
            if arg_name in args_annotations:
                arg_annotation = args_annotations[arg_name]
                param_repr.append(f"  # type: {getattr(arg_annotation, '__name__', arg_annotation)!s}")

        if param_repr:
            param_repr.extend(("\n", " " * indent))

        param_str = "".join(param_repr)
        start: str = "" if no_indent_start else " " * indent
        return f"{start}{src.__module__}.{src.__class__.__name__}({param_str})"

    def _repr_dataclass(
        self,
        src: _DataClassProto,
        indent: int = 0,
        no_indent_start: bool = False,
    ) -> str:
        """Repr dataclass.

        :param src: dataclass object to process
        :param indent: start indentation
        :param no_indent_start: do not indent open bracket and simple parameters
        :returns: Repr of dataclass.
        """
        param_repr: list[str] = []

        next_indent: int = indent + self._indent_step
        prefix: str = "\n" + " " * next_indent

        for arg_name, field in src.__dataclass_fields__.items():
            if not field.repr:
                continue
            param_repr.extend(
                (
                    prefix,
                    arg_name,
                    "=",
                    self.process_element(
                        getattr(src, arg_name),
                        indent=next_indent,
                        no_indent_start=True,
                    ),
                    ",",
                    _field_comment(
                        field.type,
                        kw_only=field.kw_only,  # type: ignore[arg-type]
                    ),
                )
            )

        if param_repr:
            param_repr.extend(("\n", " " * indent))

        param_str = "".join(param_repr)
        start: str = "" if no_indent_start else " " * indent
        return f"{start}{src.__module__}.{src.__class__.__name__}({param_str})"

    def _repr_attrs(
        self,
        src: _AttrsProto,
        indent: int = 0,
        no_indent_start: bool = False,
    ) -> str:
        """Repr attrs class instance (``attrs.define`` / ``attrs.frozen`` / ``attr.s``).

        :param src: attrs class instance to process
        :param indent: start indentation
        :param no_indent_start: do not indent open bracket and simple parameters
        :returns: Repr of attrs class instance.
        """
        param_repr: list[str] = []

        next_indent: int = indent + self._indent_step
        prefix: str = "\n" + " " * next_indent

        for field in src.__attrs_attrs__:
            if field.repr is False:
                continue
            param_repr.extend(
                (
                    prefix,
                    field.name,
                    "=",
                    self.process_element(getattr(src, field.name), indent=next_indent, no_indent_start=True),
                    ",",
                    _field_comment(getattr(field, "type", None), kw_only=getattr(field, "kw_only", False)),
                )
            )

        if param_repr:
            param_repr.extend(("\n", " " * indent))

        param_str = "".join(param_repr)
        start: str = "" if no_indent_start else " " * indent
        return f"{start}{src.__module__}.{src.__class__.__name__}({param_str})"

    @abc.abstractmethod
    def _repr_simple(
        self,
        src: Any,
        indent: int = 0,
        no_indent_start: bool = False,
    ) -> str:
        """Repr object without iteration.

        :param src: Source object
        :param indent: start indentation
        :param no_indent_start: ignore indent
        :returns: simple repr() over an object
        """

    @abc.abstractmethod
    def _repr_dict_items(
        self,
        src: dict[Any, Any],
        indent: int = 0,
    ) -> str:
        """Repr dict items.

        :param src: Object to process
        :param indent: start indentation
        :returns: repr of key/value pairs from dict
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
        :param prefix: prefix
        :param indent: start indentation
        :param no_indent_start: do not indent open bracket and simple parameters
        :param result: result of pre-formatting
        :param suffix: suffix
        :returns: formatted repr of "result" with prefix and suffix to explain type.
        """

    def _repr_iterable_items(
        self,
        src: Iterable[Any],
        indent: int = 0,
    ) -> str:
        """Repr iterable items (not designed for dicts).

        :param src: Object to process
        :param indent: start indentation
        :returns: repr of elements in iterable item
        """
        next_indent: int = indent + self._indent_step
        max_iter: int = self._max_iter
        buf: list[str] = []

        if max_iter <= 0:
            for elem in src:
                buf.extend(("\n", self.process_element(src=elem, indent=next_indent), ","))
            return "".join(buf)

        for idx, elem in enumerate(src, start=1):
            buf.extend(("\n", self.process_element(src=elem, indent=next_indent)))

            if idx == max_iter:
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

        :param src: Object to process
        :param indent: start indentation
        :param no_indent_start: do not indent open bracket and simple parameters
        :returns: formatted string
        """
        param_repr: list[str] = []

        next_indent: int = indent + self._indent_step
        prefix: str = "\n" + " " * next_indent
        arg: typing.Any | tuple[typing.Any] | tuple[str, typing.Any] | tuple[str, typing.Any, typing.Any]
        arg_name: str | None

        for arg in src.__rich_repr__():
            if isinstance(arg, tuple):
                match len(arg):
                    case 1:
                        arg_name = None
                        default = ()
                        value = arg[0]
                    case 2:
                        arg_name, value = arg
                        default = ()
                    case _:
                        arg_name, value, *default = arg  # type: ignore[assignment]

                if arg_name is not None and default and default[0] == value:
                    # standard behaviour for rich
                    continue

                repr_val = self.process_element(value, indent=next_indent, no_indent_start=True)

                if arg_name is None:
                    param_repr.extend((prefix, repr_val, ","))
                else:
                    param_repr.extend((prefix, arg_name, "=", repr_val, ","))

            else:
                param_repr.extend((prefix, self.process_element(arg, indent=next_indent, no_indent_start=True), ","))

        if param_repr:
            param_repr.extend(("\n", " " * indent))

        param_str = "".join(param_repr)
        return f"{'' if no_indent_start else ' ' * indent}{src.__module__}.{src.__class__.__name__}({param_str})"

    def process_element(
        self,
        src: Any,
        indent: int = 0,
        no_indent_start: bool = False,
    ) -> str:
        """Make a human-readable representation of an object.

        :param src: Object to process
        :param indent: start indentation
        :param no_indent_start: do not indent open bracket and simple parameters
        :returns: formatted string

        Example::

            >>> formatter = PrettyRepr()
            >>> print(formatter.process_element({'key': [1, 2, 3]}))
            {
                'key': [
                    1,
                    2,
                    3,
                ],
            }
        """
        src_type: type = type(src)

        # Fast path: scalars are always rendered by plain repr()/str(), no dispatch is required.
        if src_type in _LEAF_TYPES:
            return self._repr_simple(src=src, indent=indent, no_indent_start=no_indent_start)

        # Builtin containers (exact types) cannot carry any of the special protocols: dispatch is skipped for them.
        if src_type not in _EXACT_CONTAINER_TYPES:
            magic_method = getattr(src, self._magic_method_name, None)
            if magic_method is not None:
                return magic_method(  # type: ignore[no-any-return]
                    self,
                    indent=indent,
                    no_indent_start=no_indent_start,
                )

            # `hasattr()` probes below are inexpensive necessary conditions for the protocol match:
            # the expensive `isinstance()` over the protocol is the final authority. See `_protocol_probe`.
            if hasattr(src, _RICH_REPR_PROBE) and isinstance(src, _RichReprProto):
                return self._repr_rich(src=src, indent=indent)

            if isinstance(src, _CALLABLE_TYPES):
                return self._repr_callable(src=src, indent=indent)

            if hasattr(src, _ATTRIBUTE_HOLDER_PROBE) and isinstance(src, _AttributeHolderProto):
                return self._repr_attribute_holder(src=src, indent=indent, no_indent_start=no_indent_start)

            if isinstance(src, tuple) and hasattr(src, _NAMED_TUPLE_PROBE) and isinstance(src, _NamedTupleProto):
                return self._repr_named_tuple(src=src, indent=indent, no_indent_start=no_indent_start)

            if not isinstance(src, type):
                if (
                    hasattr(src, _DATA_CLASS_PROBE)
                    and isinstance(src, _DataClassProto)
                    and src.__dataclass_params__.repr
                ):
                    return self._repr_dataclass(src=src, indent=indent, no_indent_start=no_indent_start)

                if hasattr(src, _ATTRS_PROBE) and isinstance(src, _AttrsProto):
                    return self._repr_attrs(src=src, indent=indent, no_indent_start=no_indent_start)

            if _simple(src):
                return self._repr_simple(src=src, indent=indent, no_indent_start=no_indent_start)

        if indent >= self._max_indent or not src:
            return self._repr_simple(src=src, indent=indent, no_indent_start=no_indent_start)

        next_indent: int = indent + self._indent_step

        if isinstance(src, dict):
            if src_type is collections.Counter:
                # Counter is special: sorting by value applied due to Counter's nature
                # It's acceptable performance downgrade due to not warrantied order
                prefix, suffix = "Counter({", "})"
                result = self._repr_dict_items(
                    src=dict(sorted(src.items(), key=operator.itemgetter(1), reverse=True)),
                    indent=indent,
                )
            else:
                prefix, suffix = "{", "}"
                result = self._repr_dict_items(src=src, indent=indent)

        elif isinstance(src, collections.deque) and src.maxlen is not None:
            # not the most common case, but collections.deque also fall under next branch if no maxlen
            result = self._repr_iterable_items(src=src, indent=next_indent)
            start: str = "" if no_indent_start else " " * indent
            next_indent_str: str = " " * next_indent
            return (
                f"{start}"
                f"{src_type.__name__}(\n"
                f"{next_indent_str}({result}\n"
                f"{next_indent_str}),\n"
                f"{next_indent_str}maxlen={src.maxlen},\n"
                f"{' ' * indent})"
            )

        else:
            if isinstance(src, list):
                prefix, suffix = "[", "]"
            elif isinstance(src, tuple):
                prefix, suffix = "(", ")"
            elif isinstance(src, (set, frozenset)):
                prefix, suffix = "{", "}"
            elif isinstance(src, collections.deque):
                prefix, suffix = "deque((", "))"
            else:
                prefix, suffix = "", ""

            result = self._repr_iterable_items(src=src, indent=indent)

        if src_type in _PLAIN_RENDERED_TYPES:
            return f"{'' if no_indent_start else ' ' * indent}{prefix}{result}\n{' ' * indent}{suffix}"

        return self._repr_iterable_item(
            obj_type=src_type.__name__,
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
        """Make a human-readable representation of an object. The main entry point.

        :param src: Object to process
        :param indent: start indentation
        :param no_indent_start: do not indent open bracket and simple parameters
        :returns: formatted string

        Example::

            >>> formatter = PrettyRepr()
            >>> print(formatter({'key': 'value'}))
            {
                'key': 'value',
            }
        """
        return self.process_element(src, indent=indent, no_indent_start=no_indent_start)


class PrettyRepr(PrettyFormat):
    """Pretty repr.

    Designed for usage as __repr__ replacement on complex objects
    """

    __slots__ = ()

    _magic_method_name: ClassVar[str] = "__pretty_repr__"

    def _repr_simple(
        self,
        src: Any,
        indent: int = 0,
        no_indent_start: bool = False,
    ) -> str:
        """Repr object without iteration.

        :param src: Source object
        :param indent: start indentation
        :param no_indent_start: ignore indent
        :returns: simple repr() over an object, except strings (add prefix) and set
        """
        if no_indent_start or not indent:
            return repr(src)
        return " " * indent + repr(src)

    def _repr_dict_items(
        self,
        src: dict[Any, Any],
        indent: int = 0,
    ) -> str:
        """Repr dict items.

        :param src: Object to process
        :param indent: start indentation
        :returns: repr of key/value pairs from dict
        """
        keys_repr: list[str] = [repr(key) for key in src]
        max_len: int = max(map(len, keys_repr), default=0)
        next_indent: int = indent + self._indent_step
        prefix: str = "\n" + " " * next_indent
        buf: list[str] = []
        for key_repr, val in zip(keys_repr, src.values(), strict=True):
            buf.extend(
                (
                    prefix,
                    key_repr.ljust(max_len),
                    ": ",
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
        :param prefix: prefix
        :param indent: start indentation
        :param no_indent_start: do not indent open bracket and simple parameters
        :param result: result of pre-formatting
        :param suffix: suffix
        :returns: formatted repr of "result" with prefix and suffix to explain type.
        """
        start: str = "" if no_indent_start else " " * indent
        return f"{start}{obj_type}({prefix}{result}\n{' ' * indent}{suffix})"


class PrettyStr(PrettyFormat):
    """Pretty str.

    Designed for usage as __str__ replacement on complex objects
    """

    __slots__ = ()

    _magic_method_name: ClassVar[str] = "__pretty_str__"

    @staticmethod
    def _strings_str(
        indent: int,
        val: bytes | str,
    ) -> str:
        """Custom str for strings and binary strings.

        :param indent: Result indent
        :param val: value for repr
        :returns: indented string as `str`
        """
        if isinstance(val, bytes):
            string: str = val.decode(encoding="utf-8", errors="backslashreplace")
        else:
            string = val
        if not indent:
            return string
        return " " * indent + string

    def _repr_simple(
        self,
        src: Any,
        indent: int = 0,
        no_indent_start: bool = False,
    ) -> str:
        """Repr object without iteration.

        :param src: Source object
        :param indent: start indentation
        :param no_indent_start: ignore indent
        :returns: simple repr() over an object, except strings (decode) and set
        """
        indent = 0 if no_indent_start else indent
        if isinstance(src, (bytes, str)):
            return self._strings_str(indent=indent, val=src)
        if not indent:
            return str(src)
        return " " * indent + str(src)

    def _repr_dict_items(
        self,
        src: dict[Any, Any],
        indent: int = 0,
    ) -> str:
        """Repr dict items.

        :param src: Object to process
        :param indent: start indentation
        :returns: repr of key/value pairs from dict
        """
        keys_str: list[str] = [str(key) for key in src]
        max_len: int = max(map(len, keys_str), default=0)
        next_indent: int = indent + self._indent_step
        prefix: str = "\n" + " " * next_indent
        buf: list[str] = []
        for key_str, val in zip(keys_str, src.values(), strict=True):
            buf.extend(
                (
                    prefix,
                    key_str.ljust(max_len),
                    ": ",
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
        :param prefix: prefix
        :param indent: start indentation
        :param no_indent_start: do not indent open bracket and simple parameters
        :param result: result of pre-formatting
        :param suffix: suffix
        :returns: formatted repr of "result" with prefix and suffix to explain type.
        """
        start: str = "" if no_indent_start else " " * indent
        return f"{start}{prefix}{result}\n{' ' * indent}{suffix}"


def pretty_repr(
    src: Any,
    indent: int = 0,
    no_indent_start: bool = False,
    max_indent: int = 20,
    max_iter: int = 0,
    indent_step: int = 4,
) -> str:
    """Make human-readable repr of an object.

    :param src: Object to process
    :param indent: start indentation; all next levels are +indent_step
    :param no_indent_start: do not indent open bracket and simple parameters
    :param max_indent: maximal indent before classic repr() call
    :param max_iter: maximal number of items to iterate
    :param indent_step: a step for the next indentation level
    :returns: formatted string

    Example::

        >>> data = {'key': [1, 2, 3], 'nested': {'inner': 'value'}}
        >>> print(pretty_repr(data))
        {
            'key'   : [
                1,
                2,
                3,
            ],
            'nested': {
                'inner': 'value',
            },
        }
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
    """Make human-readable str of an object.

    :param src: Object to process
    :param indent: start indentation; all next levels are +indent_step
    :param no_indent_start: do not indent open bracket and simple parameters
    :param max_indent: maximal indent before classic repr() call
    :param max_iter: maximal number of items to log in an iterables
    :param indent_step: step for the next indentation level
    :returns: formatted string

    Example::

        >>> data = {'key': [1, 2, 3], 'nested': {'inner': 'value'}}
        >>> print(pretty_str(data))
        {
            key   : [
                1,
                2,
                3,
            ],
            nested: {
                inner: value,
            },
        }
    """
    return PrettyStr(max_indent=max_indent, max_iter=max_iter, indent_step=indent_step)(
        src=src,
        indent=indent,
        no_indent_start=no_indent_start,
    )
