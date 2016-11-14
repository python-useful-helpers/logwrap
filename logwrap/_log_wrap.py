#    Copyright 2016 Alexey Stepanov aka penguinolog

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

"""log_wrap module

This is no reason to import this submodule directly, all required methods is
available from the main module.
"""

from __future__ import absolute_import
from __future__ import unicode_literals

import functools
import logging
import sys

import logwrap as core

# pylint: disable=ungrouped-imports, no-name-in-module
if sys.version_info[0:2] > (3, 0):
    from inspect import signature
else:
    # noinspection PyUnresolvedReferences
    from funcsigs import signature
# pylint: enable=ungrouped-imports, no-name-in-module


_logger = logging.getLogger(__name__)


indent = 4
fmt = "\n{spc:<{indent}}{{key!r}}={{val}},".format(
    spc='',
    indent=indent,
).format
comment = "\n{spc:<{indent}}# {{kind!s}}:".format(spc='', indent=indent).format


def _get_func_args_repr(sig, args, kwargs, max_indent):
    """Internal helper for reducing complexity of decorator code

    :type sig: inspect.Signature
    :type max_indent: int
    :rtype: str
    """

    bound = sig.bind(*args, **kwargs).arguments

    param_str = ""

    last_kind = None
    for param in sig.parameters.values():
        if last_kind != param.kind:
            param_str += comment(kind=param.kind)
            last_kind = param.kind
        param_str += fmt(
            key=param.name,
            val=core.pretty_repr(
                src=bound.get(param.name, param.default),
                indent=indent + 4,
                no_indent_start=True,
                max_indent=max_indent,
            ),
        )
    if param_str:
        param_str += "\n"
    return param_str


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
        # Get signature _before_ call
        sig = signature(obj=func if not spec else spec)

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            """Real wrapper.

             *args and **kwargs is bound in separate helpers
             """
            args_repr = _get_func_args_repr(
                sig=sig,
                args=args,
                kwargs=kwargs,
                max_indent=max_indent,
            )

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
