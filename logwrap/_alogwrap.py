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

"""log_wrap: async part (python 3.5+).

This is no reason to import this submodule directly, all required methods is
available from the main module.
"""

from __future__ import absolute_import
from __future__ import unicode_literals

import functools
import inspect
import logging
import types
import typing

import logwrap as core

from . import _log_wrap_shared


def async_logwrap(
    log: logging.Logger=_log_wrap_shared.logger,
    log_level: int=logging.DEBUG,
    exc_level: int=logging.ERROR,
    max_indent: int=20,
    spec: types.FunctionType=None,
    blacklisted_names: typing.Iterable[str]=None,
) -> types.FunctionType:
    """Log function calls and return values. Async version.

    :param log: logger object for decorator, by default used 'logwrap'
    :type log: logging.Logger
    :param log_level: log level for successful calls
    :type log_level: int
    :param exc_level: log level for exception cases
    :type exc_level: int
    :param max_indent: maximal indent before classic repr() call.
    :type  max_indent: int
    :param spec: callable object used as spec for arguments bind.
                 This is designed for the special cases only,
                 when impossible to change signature of target object,
                 but processed/redirected signature is accessible.
                 Note: this object should provide fully compatible signature
                 with decorated function, or arguments bind will be failed!
    :type spec: types.FunctionType
    :param blacklisted_names: Blacklisted argument names.
                              Arguments with this names will be skipped in log.
    :type blacklisted_names: typing.Iterable[str]
    :return: built real decorator
    :rtype: types.FunctionType
    """
    if blacklisted_names is None:
        blacklisted_names = []

    def real_decorator(func: types.FunctionType) -> types.CoroutineType:
        """Log function calls and return values.

        This decorator could be extracted as configured from outer function.

        :param func: function to log calls from
        :type func: types.FunctionType
        :return: wrapped coroutine function
        :rtype: types.CoroutineType
        """
        # Get signature _before_ call
        sig = inspect.signature(obj=func if not spec else spec)

        # pylint: disable=missing-docstring
        # noinspection PyCompatibility
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            args_repr = _log_wrap_shared.get_func_args_repr(
                sig=sig,
                args=args,
                kwargs=kwargs,
                max_indent=max_indent,
                blacklisted_names=blacklisted_names
            )

            log.log(
                level=log_level,
                msg="Calling: \n{name!r}({arguments})".format(
                    name=func.__name__,
                    arguments=args_repr
                )
            )
            try:
                if inspect.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                log.log(
                    level=log_level,
                    msg="Done: {name!r} with result:\n{result}".format(
                        name=func.__name__,
                        result=core.pretty_repr(
                            result,
                            max_indent=max_indent,
                        )
                    )
                )
            except BaseException:
                log.log(
                    level=exc_level,
                    msg="Failed: \n{name!r}({arguments})".format(
                        name=func.__name__,
                        arguments=args_repr,
                    ),
                    exc_info=True
                )
                raise
            return result

        # pylint: enable=missing-docstring
        return wrapped

    if not isinstance(log, logging.Logger):
        func, log = log, _log_wrap_shared.logger

        return real_decorator(func)

    return real_decorator


__all__ = ('async_logwrap',)
