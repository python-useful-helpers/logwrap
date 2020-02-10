#    Copyright 2016-2020 Alexey Stepanov aka penguinolog

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
import logging
import typing

from logwrap cimport class_decorator


cdef:
    unsigned long indent


    class LogWrap(class_decorator.BaseDecorator):
        """Base class for LogWrap implementation."""

        cdef:
            public unsigned long log_level
            public unsigned long exc_level
            public unsigned long max_indent

            public bint log_call_args
            public bint log_call_args_on_exc
            public bint log_traceback
            public bint log_result_obj

            readonly object _spec
            readonly object _logger

            list __blacklisted_names
            list __blacklisted_exceptions

        cpdef object pre_process_param(self, object arg)
        cpdef str post_process_param(self, object arg, str arg_repr)

        cdef:
            str _get_func_args_repr(self, sig: inspect.Signature, tuple args, dict kwargs)
            void _make_done_record(self, logger: logging.Logger, str func_name, result: typing.Any) except *
            void _make_calling_record(self, logger: logging.Logger, str name, str arguments, str method=?) except *
            void _make_exc_record(self, logger: logging.Logger, str name, str arguments, Exception exception) except *
