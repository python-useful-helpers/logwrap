#    Copyright 2018-2020 Alexey Stepanov aka penguinolog

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

import types
import typing


cpdef tuple __all__

cdef:
    bint _known_callable(item: typing.Any)
    bint _simple(item: typing.Any)

    class ReprParameter:
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
        cdef:
            readonly unsigned long max_indent
            readonly unsigned long indent_step
            readonly str _magic_method_name

        cpdef long next_indent(self, unsigned long indent, unsigned long multiplier=?)

        cdef:
            str _repr_callable(self, src: typing.Union[types.FunctionType, types.MethodType], unsigned long indent=?)
            str _repr_simple(self, src: typing.Any, unsigned long indent=?, bint no_indent_start=?)
            str _repr_iterable_item(self, str obj_type, str prefix, unsigned long indent, bint no_indent_start, str result, str suffix)
            str _repr_iterable_items(self, src: typing.Iterable, unsigned long indent=?)
            str _repr_dict_items(self, object src: typing.Dict[typing.Any, typing.Any], unsigned long indent=?)

        cpdef str process_element(self, src: typing.Any, unsigned long indent=?, bint no_indent_start=?)

    class PrettyStr(PrettyFormat):
        cdef str _strings_str(self, unsigned long indent, val: typing.Union[bytes, str])


cpdef str pretty_repr(
    src: typing.Any,
    unsigned long indent=?,
    bint no_indent_start=?,
    unsigned long max_indent=?,
    unsigned long indent_step=?
)

cpdef  str pretty_str(
    src: typing.Any,
    unsigned long indent=?,
    bint no_indent_start=?,
    unsigned long max_indent=?,
    unsigned long indent_step=?
)
