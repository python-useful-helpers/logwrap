#    Copyright 2016-2017 Alexey Stepanov aka penguinolog

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

"""log_wrap: async part (python 3.4+).

This is no reason to import this submodule directly, all required methods is
available from the main module.
"""

from __future__ import absolute_import
from __future__ import unicode_literals

# noinspection PyCompatibility
import asyncio
import functools
import inspect
import typing


from . import _log_wrap_shared

__all__ = ('logwrap', 'LogWrap')


class LogWrap(_log_wrap_shared.BaseLogWrap):
    """Python 3.3+ version of LogWrap."""

    __slots__ = ()

    def _get_function_wrapper(
        self,
        func: typing.Callable
    ) -> typing.Callable:
        """Here should be constructed and returned real decorator.

        :param func: Wrapped function
        :type func: typing.Callable
        :return: wrapped coroutine or function
        :rtype: typing.Callable
        """
        sig = inspect.signature(obj=self._spec or func)

        # pylint: disable=missing-docstring
        # noinspection PyCompatibility,PyMissingOrEmptyDocstring
        @functools.wraps(func)
        @asyncio.coroutine
        def async_wrapper(*args, **kwargs):
            args_repr = self._get_func_args_repr(
                sig=sig,
                args=args,
                kwargs=kwargs,
            )

            try:
                self._make_calling_record(
                    name=func.__name__,
                    arguments=args_repr,
                    method='Awaiting'
                )
                result = yield from func(*args, **kwargs)
                self._make_done_record(func.__name__, result)
            except BaseException as e:
                if isinstance(e, tuple(self.blacklisted_exceptions)):
                    raise
                self._make_exc_record(name=func.__name__, arguments=args_repr)
                raise
            return result

        # noinspection PyCompatibility,PyMissingOrEmptyDocstring
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            args_repr = self._get_func_args_repr(
                sig=sig,
                args=args,
                kwargs=kwargs,
            )

            try:
                self._make_calling_record(
                    name=func.__name__,
                    arguments=args_repr
                )
                result = func(*args, **kwargs)
                self._make_done_record(func.__name__, result)
            except BaseException as e:
                if isinstance(e, tuple(self.blacklisted_exceptions)):
                    raise
                self._make_exc_record(name=func.__name__, arguments=args_repr)
                raise
            return result

        # pylint: enable=missing-docstring
        return async_wrapper if asyncio.iscoroutinefunction(func) else wrapper


logwrap = LogWrap  # lowercase decorator
