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

"""log_wrap shared code module."""

from __future__ import absolute_import
from __future__ import unicode_literals

import functools
import logging

import logwrap as core
from . import _class_decorator

__all__ = ('BaseLogWrap', )

logger = logging.getLogger(__name__)


indent = 4
fmt = "\n{spc:<{indent}}{{key!r}}={{val}},".format(
    spc='',
    indent=indent,
).format
comment = "\n{spc:<{indent}}# {{kind!s}}:".format(spc='', indent=indent).format


def _check_type(expected):
    """Check type before assign.

    :type expected: type
    """
    def deco(func):
        """Check type before assign."""
        # pylint: disable=missing-docstring
        # noinspection PyMissingOrEmptyDocstring
        @functools.wraps(func)
        def wrapper(self, val):
            if not isinstance(val, expected):
                raise TypeError(
                    'Unexpected type: {}. Should be {}.'.format(
                        val.__class__.__name__,
                        expected.__name__,
                    )
                )
            return func(self, val)

        # pylint: enable=missing-docstring
        return wrapper
    return deco

# pylint: disable=assigning-non-slot,abstract-method


# noinspection PyAbstractClass
class BaseLogWrap(_class_decorator.BaseDecorator):
    """Base class for LogWrap implementation."""

    __slots__ = (
        '__blacklisted_names',
        '__blacklisted_exceptions',
        '__logger',
        '__log_level',
        '__exc_level',
        '__max_indent',
        '__spec',
        '__log_call_args',
        '__log_call_args_on_exc',
        '__log_result_obj',
    )

    def __init__(
        self,
        log=logger,
        log_level=logging.DEBUG,
        exc_level=logging.ERROR,
        max_indent=20,
        spec=None,
        blacklisted_names=None,
        blacklisted_exceptions=None,
        log_call_args=True,
        log_call_args_on_exc=True,
        log_result_obj=True,

    ):
        """Log function calls and return values.

        :param log: logger object for decorator, by default used 'logwrap'
        :type log: typing.Union[logging.Logger, typing.Callable]
        :param log_level: log level for successful calls
        :type log_level: int
        :param exc_level: log level for exception cases
        :type exc_level: int
        :param max_indent: maximum indent before classic `repr()` call.
        :type max_indent: int
        :param spec: callable object used as spec for arguments bind.
                     This is designed for the special cases only,
                     when impossible to change signature of target object,
                     but processed/redirected signature is accessible.
                     Note: this object should provide fully compatible
                     signature with decorated function, or arguments bind
                     will be failed!
        :type spec: callable
        :param blacklisted_names: Blacklisted argument names.
                                  Arguments with this names will be skipped
                                  in log.
        :type blacklisted_names: typing.Optional[typing.Iterable[str]]
        :param blacklisted_exceptions: list of exception,
                                       which should be re-raised without
                                       producing log record.
        :type blacklisted_exceptions: typing.Optional[
                                          typing.Iterable[Exception]
                                      ]
        :param log_call_args: log call arguments before executing
                              wrapped function.
        :type log_call_args: bool
        :param log_call_args_on_exc: log call arguments if exception raised.
        :type log_call_args_on_exc: bool
        :param log_result_obj: log result of function call.
        :type log_result_obj: bool
        """
        # Typing fix:
        if blacklisted_names is None:
            self.__blacklisted_names = []
        else:
            self.__blacklisted_names = list(blacklisted_names)
        if blacklisted_exceptions is None:
            self.__blacklisted_exceptions = []
        else:
            self.__blacklisted_exceptions = list(blacklisted_exceptions)

        if not isinstance(log, logging.Logger):
            func, self.__logger = log, logger
        else:
            func, self.__logger = None, log
        super(BaseLogWrap, self).__init__(func=func)

        self.__log_level = log_level
        self.__exc_level = exc_level
        self.__max_indent = max_indent
        self.__spec = spec or self._func
        self.__log_call_args = log_call_args
        self.__log_call_args_on_exc = log_call_args_on_exc
        self.__log_result_obj = log_result_obj

        # We are not interested to pass any arguments to object

    @property
    def log_level(self):
        """Log level for normal behavior.

        :rtype: int
        """
        return self.__log_level

    @log_level.setter
    @_check_type(int)
    def log_level(self, val):
        """Log level for normal behavior.

        :type val: int
        """
        self.__log_level = val

    @property
    def exc_level(self):
        """Log level for exceptions.

        :rtype: int
        """
        return self.__exc_level

    @exc_level.setter
    @_check_type(int)
    def exc_level(self, val):
        """Log level for exceptions.

        :type val: int
        """
        self.__exc_level = val

    @property
    def max_indent(self):
        """Maximum indentation.

        :rtype: int
        """
        return self.__max_indent

    @max_indent.setter
    @_check_type(int)
    def max_indent(self, val):
        """Maximum indentation.

        :type val: int
        """
        self.__max_indent = val

    @property
    def blacklisted_names(self):
        """List of arguments names to ignore in log.

        :rtype: typing.List[str]
        """
        return self.__blacklisted_names

    @property
    def blacklisted_exceptions(self):
        """List of exceptions to re-raise without log.

        :rtype: typing.List[Exception]
        """
        return self.__blacklisted_exceptions

    @property
    def log_call_args(self):
        """Flag: log call arguments before call.

        :rtype: bool
        """
        return self.__log_call_args

    @log_call_args.setter
    @_check_type(bool)
    def log_call_args(self, val):
        """Flag: log call arguments before call.

        :type val: bool
        """
        self.__log_call_args = val

    @property
    def log_call_args_on_exc(self):
        """Flag: log call arguments on exception.

        :rtype: bool
        """
        return self.__log_call_args_on_exc

    @log_call_args_on_exc.setter
    @_check_type(bool)
    def log_call_args_on_exc(self, val):
        """Flag: log call arguments on exception.

        :type val: bool
        """
        self.__log_call_args_on_exc = val

    @property
    def log_result_obj(self):
        """Flag: log result object.

        :rtype: bool
        """
        return self.__log_result_obj

    @log_result_obj.setter
    @_check_type(bool)
    def log_result_obj(self, val):
        """Flag: log result object.

        :type val: bool
        """
        self.__log_result_obj = val

    @property
    def _logger(self):
        """logger instance.

        :rtype: logging.Logger
        """
        return self.__logger

    @property
    def _spec(self):
        """Spec for function arguments.

        :rtype: typing.Callable
        """
        return self.__spec

    def __repr__(self):
        """Repr for debug purposes."""
        return (
            "{cls}("
            "log={self._logger}, "
            "log_level={self.log_level}, "
            "exc_level={self.exc_level}, "
            "max_indent={self.max_indent}, "
            "spec={spec}, "
            "blacklisted_names={self.blacklisted_names}, "
            "blacklisted_exceptions={self.blacklisted_exceptions}, "
            "log_call_args={self.log_call_args}, "
            "log_call_args_on_exc={self.log_call_args_on_exc}, "
            "log_result_obj={self.log_result_obj}, )".format(
                cls=self.__class__.__name__,
                self=self,
                spec=self._spec
            )
        )

    def _get_func_args_repr(self, sig, args, kwargs):
        """Internal helper for reducing complexity of decorator code.

        :type sig: inspect.Signature
        :type args: tuple
        :type kwargs: dict
        :rtype: str
        """
        if not (self.log_call_args or self.log_call_args_on_exc):
            return ''

        bound = sig.bind(*args, **kwargs).arguments

        param_str = ""

        last_kind = None
        for param in sig.parameters.values():
            if param.name in self.blacklisted_names:
                continue

            if last_kind != param.kind:
                param_str += comment(kind=param.kind)
                last_kind = param.kind
            param_str += fmt(
                key=param.name,
                val=core.pretty_repr(
                    src=bound.get(param.name, param.default),
                    indent=indent + 4,
                    no_indent_start=True,
                    max_indent=self.max_indent,
                ),
            )
        if param_str:
            param_str += "\n"
        return param_str

    def _make_done_record(self, func_name, result):
        """Construct success record.

        :type func_name: str
        :type result: typing.Any
        """
        msg = "Done: {name!r}".format(name=func_name)

        if self.log_result_obj:
            msg += " with result:\n{result}".format(
                result=core.pretty_repr(
                    result,
                    max_indent=self.max_indent,
                )
            )
        self._logger.log(
            level=self.log_level,
            msg=msg
        )

    def _make_calling_record(self, name, arguments, method='Calling'):
        """Make log record before execution.

        :type name: str
        :type arguments: str
        :type method: str
        """
        self._logger.log(
            level=self.log_level,
            msg="{method}: \n{name!r}({arguments})".format(
                method=method,
                name=name,
                arguments=arguments if self.log_call_args else ''
            )
        )

    def _make_exc_record(self, name, arguments):
        """Make log record if exception raised.

        :type name: str
        :type arguments: str
        """
        self._logger.log(
            level=self.exc_level,
            msg="Failed: \n{name!r}({arguments})".format(
                name=name,
                arguments=arguments if self.log_call_args_on_exc else '',
            ),
            exc_info=True
        )


# pylint: enable=assigning-non-slot, abstract-method
