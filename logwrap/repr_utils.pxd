#    Copyright 2018-2022 Alexey Stepanov aka penguinolog

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

# Standard Library
import dataclasses
import types
import typing
from collections.abc import Iterable


@typing.runtime_checkable
class _AttributeHolderProto(typing.Protocol):
    __slots__ = ()

    def _get_kwargs(self) -> list[tuple[str, typing.Any]]:
        """Protocol stub."""

    def _get_args(self) -> list[str]:
        """Protocol stub."""


@typing.runtime_checkable
class _NamedTupleProto(typing.Protocol):
    __slots__ = ()

    def _asdict(self) -> dict[str, typing.Any]:
        """Protocol stub."""

    def __getnewargs__(self) -> tuple[typing.Any, ...]:
        """Protocol stub."""

    def _replace(self, **kwds: dict[str, typing.Any]) -> _NamedTupleProto:
        """Protocol stub."""

    @classmethod
    def _make(cls, iterable: Iterable[typing.Any]) -> _NamedTupleProto:
        """Protocol stub."""


@typing.runtime_checkable
class _DataClassProto(typing.Protocol):
    __slots__ = ()

    __dataclass_params__: dataclasses._DataclassParams  # type: ignore[name-defined]
    __dataclass_fields__: dict[str, dataclasses.Field[typing.Any]] = {}


cdef:
    bint _known_callable(item: typing.Any)
    bint _simple(item: typing.Any)

    class ReprParameter:
        """Parameter wrapper wor repr and str operations over signature."""

        cdef:
            readonly object POSITIONAL_ONLY
            readonly object POSITIONAL_OR_KEYWORD
            readonly object VAR_POSITIONAL
            readonly object KEYWORD_ONLY
            readonly object VAR_KEYWORD
            readonly object empty

            readonly object parameter
            readonly str name
            readonly object annotation
            readonly object kind
            readonly object value

    list _prepare_repr(func: typing.Union[types.FunctionType, types.MethodType])

    class PrettyFormat:
        """Pretty Formatter.

        Designed for usage as __repr__ and __str__ replacement on complex objects
        """

        cdef:
            readonly unsigned long max_indent
            readonly unsigned long indent_step
            readonly str _magic_method_name

        # noinspection PyMissingOrEmptyDocstring
        cpdef unsigned long next_indent(self, unsigned long indent, unsigned long multiplier=?)

        cdef:
            str _repr_callable(self, src: typing.Union[types.FunctionType, types.MethodType], unsigned long indent=?)
            str _repr_attribute_holder(self, src: _AttributeHolderProto, unsigned long indent=?, bint no_indent_start=?)
            str _repr_named_tuple(self, src: _NamedTupleProto, unsigned long indent=?, bint no_indent_start=?)
            str _repr_dataclass(self, src: _DataClassProto, unsigned long indent=?, bint no_indent_start=?)
            str _repr_simple(self, src: typing.Any, unsigned long indent=?, bint no_indent_start=?)
            str _repr_iterable_item(self, str obj_type, str prefix, unsigned long indent, bint no_indent_start, str result, str suffix)
            str _repr_iterable_items(self, src: typing.Iterable, unsigned long indent=?)
            str _repr_dict_items(self, object src: typing.Dict[typing.Any, typing.Any], unsigned long indent=?)

        # noinspection PyMissingOrEmptyDocstring
        cpdef str process_element(self, src: typing.Any, unsigned long indent=?, bint no_indent_start=?)

    class PrettyStr(PrettyFormat):
        """Pretty str.

        Designed for usage as __str__ replacement on complex objects
        """

        cdef str _strings_str(self, unsigned long indent, val: typing.Union[bytes, str])


# noinspection PyMissingOrEmptyDocstring
cpdef str pretty_repr(
    src: typing.Any,
    unsigned long indent=?,
    bint no_indent_start=?,
    unsigned long max_indent=?,
    unsigned long indent_step=?
)

# noinspection PyMissingOrEmptyDocstring
cpdef str pretty_str(
    src: typing.Any,
    unsigned long indent=?,
    bint no_indent_start=?,
    unsigned long max_indent=?,
    unsigned long indent_step=?
)
