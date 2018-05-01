#    Copyright 2016-2018 Alexey Stepanov aka penguinolog

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
import inspect  # noqa # pylint: disable=unused-import
import logging
import typing  # noqa # pylint: disable=unused-import

import six  # noqa # pylint: disable=unused-import

import logwrap as core
from . import _class_decorator

# pylint: disable=ungrouped-imports, no-name-in-module
if six.PY3:  # pragma: no cover
    from inspect import formatannotation
    from inspect import Parameter
    from inspect import Signature  # noqa # pylint: disable=unused-import
else:  # pragma: no cover
    # noinspection PyUnresolvedReferences,PyProtectedMember,PyPackageRequirements
    from funcsigs import formatannotation
    # noinspection PyUnresolvedReferences,PyPackageRequirements
    from funcsigs import Parameter
    # noinspection PyUnresolvedReferences,PyPackageRequirements
    from funcsigs import Signature  # noqa # pylint: disable=unused-import
# pylint: enable=ungrouped-imports, no-name-in-module

__all__ = ('BaseLogWrap', 'BoundParameter', 'bind_args_kwargs')

logger = logging.getLogger(__name__)  # type: logging.Logger


indent = 4
fmt = "\n{spc:<{indent}}{{key!r}}={{val}},".format(
    spc='',
    indent=indent,
).format
comment = "\n{spc:<{indent}}# {{kind!s}}:".format(spc='', indent=indent).format


def _check_type(expected):  # type: (typing.Type) -> typing.Callable
    """Check type before assign.

    :type expected: type
    """
    def deco(func):  # type: (typing.Callable) -> typing.Callable
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


class BoundParameter(object):
    """Parameter-like object store BOUND with value parameter.

    .. versionadded:: 3.3.0
    """

    __slots__ = (
        '_parameter',
        '_value'
    )

    POSITIONAL_ONLY = Parameter.POSITIONAL_ONLY
    POSITIONAL_OR_KEYWORD = Parameter.POSITIONAL_OR_KEYWORD
    VAR_POSITIONAL = Parameter.VAR_POSITIONAL
    KEYWORD_ONLY = Parameter.KEYWORD_ONLY
    VAR_KEYWORD = Parameter.VAR_KEYWORD

    empty = Parameter.empty

    def __init__(
        self,
        parameter,  # type: Parameter
        value=Parameter.empty  # type: typing.Any
    ):  # type: (...) -> None
        """Parameter-like object store BOUND with value parameter.

        :param parameter: parameter from signature
        :type parameter: inspect.Parameter
        :param value: parameter real value
        :type value: typing.Any
        :raises ValueError: No default value and no value
        """
        self._parameter = parameter

        if value is self.empty:
            if parameter.default is self.empty and parameter.kind not in (self.VAR_POSITIONAL, self.VAR_KEYWORD):
                raise ValueError('Value is not set and no default value')
            self._value = parameter.default
        else:
            self._value = value

    @property
    def parameter(self):  # type: () -> Parameter
        """Parameter object."""
        return self._parameter

    @property
    def name(self):  # type: () -> typing.Union[None, str]
        """Parameter name."""
        return self.parameter.name

    @property
    def default(self):  # type: () -> typing.Any
        """Parameter default value."""
        return self.parameter.default

    @property
    def annotation(self):  # type: () -> typing.Union[Parameter.empty, str]
        """Parameter annotation."""
        return self.parameter.annotation

    @property
    def kind(self):  # type: () -> int
        """Parameter kind."""
        return self.parameter.kind

    @property
    def value(self):  # type: () -> typing.Any
        """Parameter value."""
        return self._value

    def __hash__(self):  # pragma: no cover
        """Block hashing.

        :raises TypeError: Not hashable.
        """
        msg = "unhashable type: '{0}'".format(self.__class__.__name__)
        raise TypeError(msg)

    def __str__(self):
        """Debug purposes."""
        as_str = self.name

        # POSITIONAL_ONLY is only in precompiled functions
        if self.kind == self.POSITIONAL_ONLY:  # pragma: no cover
            as_str = '' if as_str is None else '<{as_str}>'.format(as_str=as_str)

        # Add annotation if applicable (python 3 only)
        if self.annotation is not self.empty:  # pragma: no cover
            as_str += ': {annotation!s}'.format(annotation=formatannotation(self.annotation))

        value = self.value
        if self.empty == value:
            if self.VAR_POSITIONAL == self.kind:
                value = ()
            elif self.VAR_KEYWORD == self.kind:
                value = {}

        as_str += '={value!r}'.format(value=value)

        if self.default is not self.empty:
            as_str += '  # {self.default!r}'.format(self=self)

        if self.kind == self.VAR_POSITIONAL:
            as_str = '*' + as_str
        elif self.kind == self.VAR_KEYWORD:
            as_str = '**' + as_str

        return as_str

    def __repr__(self):
        """Debug purposes."""
        return '<{} "{}">'.format(self.__class__.__name__, self)


def bind_args_kwargs(
    sig,  # type: Signature
    *args,
    **kwargs
):  # type: (...) -> typing.Iterator[BoundParameter]
    """Bind *args and **kwargs to signature and get Bound Parameters.

    :param sig: source signature
    :type sig: Signature
    :return: Iterator for bound parameters with all information about it
    :rtype: typing.Iterator[BoundParameter]

    .. versionadded:: 3.3.0
    """
    bound = sig.bind(*args, **kwargs).arguments
    parameters = list(sig.parameters.values())
    for param in parameters:
        yield BoundParameter(
            parameter=param,
            value=bound.get(param.name, param.default)
        )


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
        func=None,  # type: typing.Optional[typing.Callable]
        log=logger,  # type: logging.Logger
        log_level=logging.DEBUG,  # type: int
        exc_level=logging.ERROR,  # type: int
        max_indent=20,  # type: int
        spec=None,  # type: typing.Optional[typing.Callable]
        blacklisted_names=None,  # type: typing.Optional[typing.Iterable[str]]
        blacklisted_exceptions=None,  # type: typing.Optional[typing.Iterable[Exception]]
        log_call_args=True,  # type: bool
        log_call_args_on_exc=True,  # type: bool
        log_result_obj=True,  # type: bool
    ):  # type: (...) -> None
        """Log function calls and return values.

        :param func: function to wrap
        :type func: typing.Optional[typing.Callable]
        :param log: logger object for decorator, by default used 'logwrap'
        :type log: logging.Logger
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
        :type spec: typing.Optional[typing.Callable]
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

        .. versionchanged:: 3.3.0 Extract func from log and do not use Union.
        """
        super(BaseLogWrap, self).__init__(func=func)

        # Typing fix:
        if blacklisted_names is None:
            self.__blacklisted_names = []  # type: typing.List[str]
        else:
            self.__blacklisted_names = list(blacklisted_names)
        if blacklisted_exceptions is None:
            self.__blacklisted_exceptions = []  # type: typing.List[Exception]
        else:
            self.__blacklisted_exceptions = list(blacklisted_exceptions)

        self.__logger = log

        self.__log_level = log_level
        self.__exc_level = exc_level
        self.__max_indent = max_indent
        self.__spec = spec or self._func
        self.__log_call_args = log_call_args
        self.__log_call_args_on_exc = log_call_args_on_exc
        self.__log_result_obj = log_result_obj

        # We are not interested to pass any arguments to object

    @property
    def log_level(self):  # type: () -> int
        """Log level for normal behavior.

        :rtype: int
        """
        return self.__log_level

    @log_level.setter
    @_check_type(int)
    def log_level(self, val):  # type: (int) -> None
        """Log level for normal behavior.

        :type val: int
        """
        self.__log_level = val

    @property
    def exc_level(self):  # type: () -> int
        """Log level for exceptions.

        :rtype: int
        """
        return self.__exc_level

    @exc_level.setter
    @_check_type(int)
    def exc_level(self, val):  # type: (int) -> None
        """Log level for exceptions.

        :type val: int
        """
        self.__exc_level = val

    @property
    def max_indent(self):  # type: () -> int
        """Maximum indentation.

        :rtype: int
        """
        return self.__max_indent

    @max_indent.setter
    @_check_type(int)
    def max_indent(self, val):  # type: (int) -> None
        """Maximum indentation.

        :type val: int
        """
        self.__max_indent = val

    @property
    def blacklisted_names(self):  # type: () -> typing.List[str]
        """List of arguments names to ignore in log.

        :rtype: typing.List[str]
        """
        return self.__blacklisted_names

    @property
    def blacklisted_exceptions(
        self
    ):  # type: () -> typing.List[Exception]
        """List of exceptions to re-raise without log.

        :rtype: typing.List[Exception]
        """
        return self.__blacklisted_exceptions

    @property
    def log_call_args(self):  # type: () -> bool
        """Flag: log call arguments before call.

        :rtype: bool
        """
        return self.__log_call_args

    @log_call_args.setter
    @_check_type(bool)
    def log_call_args(self, val):  # type: (bool) -> None
        """Flag: log call arguments before call.

        :type val: bool
        """
        self.__log_call_args = val

    @property
    def log_call_args_on_exc(self):  # type: () -> bool
        """Flag: log call arguments on exception.

        :rtype: bool
        """
        return self.__log_call_args_on_exc

    @log_call_args_on_exc.setter
    @_check_type(bool)
    def log_call_args_on_exc(self, val):  # type: (bool) -> None
        """Flag: log call arguments on exception.

        :type val: bool
        """
        self.__log_call_args_on_exc = val

    @property
    def log_result_obj(self):  # type: () -> bool
        """Flag: log result object.

        :rtype: bool
        """
        return self.__log_result_obj

    @log_result_obj.setter
    @_check_type(bool)
    def log_result_obj(self, val):  # type: (bool) -> None
        """Flag: log result object.

        :type val: bool
        """
        self.__log_result_obj = val

    @property
    def _logger(self):  # type: () -> logging.Logger
        """logger instance.

        :rtype: logging.Logger
        """
        return self.__logger

    @property
    def _spec(self):  # type: () -> typing.Callable
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

    @staticmethod
    def _bind_args_kwargs(
        sig,  # type: Signature
        *args,
        **kwargs
    ):  # type: (...) -> typing.Iterator[BoundParameter]
        """Bind *args and **kwargs to signature and get Bound Parameters.

        :param sig: source signature
        :type sig: Signature
        :return: Iterator for bound parameters with all information about it
        :rtype: typing.Iterator[BoundParameter]

        .. versionadded:: 3.3.0
        """
        return bind_args_kwargs(sig, *args, **kwargs)

    # noinspection PyMethodMayBeStatic
    def pre_process_param(  # pylint: disable=no-self-use
        self,
        arg,  # type: BoundParameter
    ):  # type: (...) -> typing.Union[BoundParameter, typing.Tuple[BoundParameter, typing.Any], None]
        """Process parameter for the future logging.

        :param arg: bound parameter
        :type arg: BoundParameter
        :return: value, value override for logging or None if argument should not be logged.
        :rtype: typing.Union[BoundParameter, typing.Tuple[BoundParameter, typing.Any], None]

        Override this method if some modifications required for parameter value before logging

        .. versionadded:: 3.3.0
        """
        return arg

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def post_process_param(  # pylint: disable=no-self-use,unused-argument
        self,
        arg,  # type: BoundParameter
        arg_repr  # type: six.text_type
    ):  # type: (...) -> six.text_type
        """Process parameter for the future logging.

        :param arg: bound parameter
        :type arg: BoundParameter
        :param arg_repr: repr for value
        :type arg_repr: six.text_type
        :return: processed repr for value
        :rtype: six.text_type

        Override this method if some modifications required for result of repr() over parameter

        .. versionadded:: 3.3.0
        """
        return arg_repr

    def _get_func_args_repr(
        self,
        sig,  # type: inspect.Signature
        args,  # type: typing.Tuple
        kwargs  # type: typing.Dict[str, typing.Any]
    ):  # type: (...) -> six.text_type
        """Internal helper for reducing complexity of decorator code.

        :type sig: inspect.Signature
        :type args: tuple
        :type kwargs: dict
        :rtype: str

        .. versionchanged:: 3.3.0 Use pre- and post- processing of params during execution
        """
        if not (self.log_call_args or self.log_call_args_on_exc):
            return ''

        param_str = ""

        last_kind = None
        for param in self._bind_args_kwargs(sig, *args, **kwargs):
            if param.name in self.blacklisted_names:
                continue

            preprocessed = self.pre_process_param(param)
            if preprocessed is None:
                continue

            if isinstance(preprocessed, (tuple, list)):
                param, value = preprocessed
            else:
                value = param.value

            if param.empty == value:
                if param.VAR_POSITIONAL == param.kind:
                    value = ()
                elif param.VAR_KEYWORD == param.kind:
                    value = {}

            val = core.pretty_repr(
                src=value,
                indent=indent + 4,
                no_indent_start=True,
                max_indent=self.max_indent,
            )

            val = self.post_process_param(param, val)

            if last_kind != param.kind:
                param_str += comment(kind=param.kind)
                last_kind = param.kind

            param_str += fmt(
                key=param.name,
                val=val,
            )
        if param_str:
            param_str += "\n"
        return param_str

    def _make_done_record(
        self,
        func_name,  # type: str
        result  # type: typing.Any
    ):  # type: (...) -> None
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

    def _make_calling_record(
        self,
        name,  # type: str
        arguments,  # type: str
        method='Calling'  # type: str
    ):  # type: (...) -> None
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

    def _make_exc_record(
        self,
        name,  # type: str
        arguments  # type: str
    ):  # type: (...) -> None
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
