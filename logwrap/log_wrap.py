#    Copyright 2016 Mirantis, Inc.
#    Copyright 2016 Alexey Stepanov aka penguinolog
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

"""log_wrap module

This is no reason to import this submodule directly, all required methods is
available from the main module.
"""

from __future__ import absolute_import
from __future__ import unicode_literals

import functools
import logging

import logwrap as core


_logger = logging.getLogger(__name__)


def logwrap(
        log=_logger,
        log_level=logging.DEBUG,
        exc_level=logging.ERROR,
        max_indent=20,
        spec=None,
):
    """Log function calls and return values

    :param log: logger object for decorator, by default used 'logwrap'
    :type log: logging.Logger
    :param log_level: log level for successful calls
    :type log_level: int
    :param exc_level: log level for exception cases
    :type exc_level: int
    :param max_indent: maximal indent before classic repr() call.
    :type max_indent: int
    :param spec: callable object used as spec for arguments bind.
                 This is designed for the special cases only,
                 when impossible to change signature of target object,
                 but processed/redirected signature is accessible.
                 Note: this object should provide fully compatible signature
                 with decorated function, or arguments bind will be failed!
    :type spec: callable
    :return: built real decorator
    :rtype: callable
    """
    def real_decorator(func):
        """Log function calls and return values

        This decorator could be extracted as configured from outer function.

        :param func: function to log calls from
        :type func: callable
        :return: wrapped function
        :rtype: callable
        """
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            """Real wrapper.

             *args and **kwargs is bound in separate helpers
             """
            if not spec:
                call_args = core.get_call_args(func, *args, **kwargs)
            else:
                call_args = core.get_call_args(spec, *args, **kwargs)
            args_repr = ""
            if len(call_args) > 0:
                args_repr = "\n    " + "\n    ".join((
                    "{key!r}={val},".format(
                        key=key,
                        val=core.pretty_repr(
                            val,
                            indent=8,
                            max_indent=max_indent,
                            no_indent_start=True,
                        ),
                    )
                    for key, val in call_args.items())
                ) + '\n'
            log.log(
                level=log_level,
                msg="Calling: \n{name!r}({arguments})".format(
                    name=func.__name__,
                    arguments=args_repr
                )
            )
            try:
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
        return wrapped

    if not isinstance(log, logging.Logger):
        func, log = log, _logger
        return real_decorator(func)

    return real_decorator

__all__ = ['logwrap']
