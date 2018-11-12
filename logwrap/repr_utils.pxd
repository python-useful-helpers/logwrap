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

import types
import typing


cdef:
    class PrettyFormat:
        cdef:
            readonly unsigned int max_indent
            readonly unsigned int indent_step
            readonly str _magic_method_name

        cpdef int next_indent(self, unsigned int indent, unsigned int multiplier=?)

        cdef:
            str _repr_callable(self, src: typing.Union[types.FunctionType, types.MethodType], unsigned int indent=?)
            str _repr_simple(self, src: typing.Any, unsigned int indent=?, bint no_indent_start=?)
            str _repr_iterable_item(self, bint nl, str obj_type, str prefix, unsigned int indent, str result, str suffix)

        cpdef str process_element(self, src: typing.Any, unsigned int indent=?, bint no_indent_start=?)

    class PrettyRepr(PrettyFormat):
        cdef str _strings_repr(self, unsigned int indent, val: typing.Union[bytes, str])

    class PrettyStr(PrettyFormat):
        cdef str _strings_str(self, unsigned int indent, val: typing.Union[bytes, str])


cpdef str pretty_repr(
    src: typing.Any,
    unsigned int indent=?,
    bint no_indent_start=?,
    unsigned int max_indent=?,
    unsigned int indent_step=?
)

cpdef  str pretty_str(
    src: typing.Any,
    unsigned int indent=?,
    bint no_indent_start=?,
    unsigned int max_indent=?,
    unsigned int indent_step=?
)
