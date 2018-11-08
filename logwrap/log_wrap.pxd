#    Copyright 2016-2018 Alexey Stepanov aka penguinolog

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

"""log_wrap shared code module."""

import inspect
import typing

from logwrap cimport class_decorator


cdef unsigned int indent


cdef str pretty_repr(
    src: typing.Any,
    unsigned int indent=?,
    bint no_indent_start=?,
    unsigned int max_indent=?,
    unsigned int indent_step=?
)


cdef class LogWrap(class_decorator.BaseDecorator):
    """Base class for LogWrap implementation."""

    cdef public unsigned int log_level
    cdef public unsigned int exc_level
    cdef public unsigned int max_indent

    cdef public bint log_call_args
    cdef public bint log_call_args_on_exc
    cdef public bint log_traceback
    cdef public bint log_result_obj

    cdef readonly object _spec
    cdef readonly object _logger

    cdef list __blacklisted_names
    cdef list __blacklisted_exceptions

    cdef str _get_func_args_repr(
        self, sig: inspect.Signature, tuple args, dict kwargs
    )
    cdef void _make_done_record(self, str func_name, result: typing.Any)
    cdef void _make_calling_record(self, str name, str arguments, str method=?)
    cdef void _make_exc_record(self, str name, str arguments)
