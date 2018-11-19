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

import asyncio
import functools
import inspect
import logging
import sys
import traceback
import typing
import warnings

import logwrap as core
from . import class_decorator


__all__ = ("LogWrap", "logwrap", "BoundParameter", "bind_args_kwargs")

logger = logging.getLogger("logwrap")  # type: logging.Logger


indent = 4
fmt = "\n{spc:<{indent}}{{key!r}}={{val}},{{annotation}}".format(spc="", indent=indent).format
comment = "\n{spc:<{indent}}# {{kind!s}}:".format(spc="", indent=indent).format


class BoundParameter(inspect.Parameter):
    """Parameter-like object store BOUND with value parameter.

    .. versionadded:: 3.3.0
    .. versionchanged:: 5.3.1 subclass inspect.Parameter
    """

    __slots__ = ("_value",)

    def __init__(self, parameter: inspect.Parameter, value: typing.Any = inspect.Parameter.empty) -> None:
        """Parameter-like object store BOUND with value parameter.

        :param parameter: parameter from signature
        :type parameter: inspect.Parameter
        :param value: parameter real value
        :type value: typing.Any
        :raises ValueError: No default value and no value
        """
        super(BoundParameter, self).__init__(
            name=parameter.name, kind=parameter.kind, default=parameter.default, annotation=parameter.annotation
        )

        if value is self.empty:
            if parameter.default is self.empty and parameter.kind not in (self.VAR_POSITIONAL, self.VAR_KEYWORD):
                raise ValueError("Value is not set and no default value")
            self._value = parameter.default
        else:
            self._value = value

    @property
    def parameter(self) -> inspect.Parameter:
        """Parameter object."""
        warnings.warn("BoundParameter is subclass of `inspect.Parameter`", DeprecationWarning)
        return self

    @property
    def value(self) -> typing.Any:
        """Parameter value."""
        return self._value

    def __str__(self) -> str:
        """Debug purposes."""
        # POSITIONAL_ONLY is only in precompiled functions
        if self.kind == self.POSITIONAL_ONLY:  # pragma: no cover
            as_str = "" if self.name is None else "<{as_str}>".format(as_str=self.name)
        else:
            as_str = self.name or ""

        # Add annotation if applicable (python 3 only)
        if self.annotation is not self.empty:  # pragma: no cover
            as_str += ": {annotation!s}".format(annotation=inspect.formatannotation(self.annotation))

        value = self.value
        if self.empty is value:
            if self.VAR_POSITIONAL == self.kind:
                value = ()
            elif self.VAR_KEYWORD == self.kind:
                value = {}

        as_str += "={value!r}".format(value=value)

        if self.default is not self.empty:
            as_str += "  # {self.default!r}".format(self=self)

        if self.kind == self.VAR_POSITIONAL:
            as_str = "*" + as_str
        elif self.kind == self.VAR_KEYWORD:
            as_str = "**" + as_str

        return as_str

    def __repr__(self) -> str:
        """Debug purposes."""
        return '<{} "{}">'.format(self.__class__.__name__, self)


def bind_args_kwargs(sig: inspect.Signature, *args: typing.Any, **kwargs: typing.Any) -> typing.List[BoundParameter]:
    """Bind *args and **kwargs to signature and get Bound Parameters.

    :param sig: source signature
    :type sig: inspect.Signature
    :param args: not keyworded arguments
    :type args: typing.Any
    :param kwargs: keyworded arguments
    :type kwargs: typing.Any
    :return: Iterator for bound parameters with all information about it
    :rtype: typing.List[BoundParameter]

    .. versionadded:: 3.3.0
    .. versionchanged:: 5.3.1 return list
    """
    result = []
    bound = sig.bind(*args, **kwargs).arguments
    for param in sig.parameters.values():
        result.append(BoundParameter(parameter=param, value=bound.get(param.name, param.default)))
    return result


# pylint: disable=assigning-non-slot,abstract-method
# noinspection PyAbstractClass
class LogWrap(class_decorator.BaseDecorator):
    """Base class for LogWrap implementation."""

    __slots__ = (
        "__blacklisted_names",
        "__blacklisted_exceptions",
        "__logger",
        "__log_level",
        "__exc_level",
        "__max_indent",
        "__spec",
        "__log_call_args",
        "__log_call_args_on_exc",
        "__log_traceback",
        "__log_result_obj",
    )

    def __init__(
        self,
        func: typing.Optional[typing.Callable] = None,
        *,
        log: logging.Logger = logger,
        log_level: int = logging.DEBUG,
        exc_level: int = logging.ERROR,
        max_indent: int = 20,
        spec: typing.Optional[typing.Callable] = None,
        blacklisted_names: typing.Optional[typing.Iterable[str]] = None,
        blacklisted_exceptions: typing.Optional[typing.Iterable[typing.Type[Exception]]] = None,
        log_call_args: bool = True,
        log_call_args_on_exc: bool = True,
        log_traceback: bool = True,
        log_result_obj: bool = True
    ) -> None:
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
        :param blacklisted_names: Blacklisted argument names. Arguments with this names will be skipped in log.
        :type blacklisted_names: typing.Optional[typing.Iterable[str]]
        :param blacklisted_exceptions: list of exception, which should be re-raised without producing log record.
        :type blacklisted_exceptions: typing.Optional[typing.Iterable[typing.Type[Exception]]]
        :param log_call_args: log call arguments before executing wrapped function.
        :type log_call_args: bool
        :param log_call_args_on_exc: log call arguments if exception raised.
        :type log_call_args_on_exc: bool
        :param log_traceback: log traceback on excaption in addition to failure info
        :type log_traceback: bool
        :param log_result_obj: log result of function call.
        :type log_result_obj: bool

        .. versionchanged:: 3.3.0 Extract func from log and do not use Union.
        .. versionchanged:: 5.1.0 log_traceback parameter
        """
        super(LogWrap, self).__init__(func=func)

        # Typing fix:
        if blacklisted_names is None:
            self.__blacklisted_names = []  # type: typing.List[str]
        else:
            self.__blacklisted_names = list(blacklisted_names)
        if blacklisted_exceptions is None:
            self.__blacklisted_exceptions = []  # type: typing.List[typing.Type[Exception]]
        else:
            self.__blacklisted_exceptions = list(blacklisted_exceptions)

        self.__logger = log

        self.__log_level = log_level
        self.__exc_level = exc_level
        self.__max_indent = max_indent
        self.__spec = spec or self._func
        self.__log_call_args = log_call_args
        self.__log_call_args_on_exc = log_call_args_on_exc
        self.__log_traceback = log_traceback
        self.__log_result_obj = log_result_obj

        # We are not interested to pass any arguments to object

    @property
    def log_level(self) -> int:
        """Log level for normal behavior.

        :rtype: int
        """
        return self.__log_level

    @log_level.setter
    def log_level(self, val: int) -> None:
        """Log level for normal behavior.

        :param val: log level to use for calls and returns
        :type val: int
        :raises TypeError: log level is not integer
        """
        if not isinstance(val, int):
            raise TypeError("Unexpected type: {}. Should be {}.".format(val.__class__.__name__, int.__name__))
        self.__log_level = val

    @property
    def exc_level(self) -> int:
        """Log level for exceptions.

        :rtype: int
        """
        return self.__exc_level

    @exc_level.setter
    def exc_level(self, val: int) -> None:
        """Log level for exceptions.

        :param val: log level to use for captured exceptions
        :type val: int
        :raises TypeError: log level is not integer
        """
        if not isinstance(val, int):
            raise TypeError("Unexpected type: {}. Should be {}.".format(val.__class__.__name__, int.__name__))
        self.__exc_level = val

    @property
    def max_indent(self) -> int:
        """Maximum indentation.

        :rtype: int
        """
        return self.__max_indent

    @max_indent.setter
    def max_indent(self, val: int) -> None:
        """Maximum indentation.

        :param val: Maximal indentation before use of simple repr()
        :type val: int
        :raises TypeError: indent is not integer
        """
        if not isinstance(val, int):
            raise TypeError("Unexpected type: {}. Should be {}.".format(val.__class__.__name__, int.__name__))
        self.__max_indent = val

    @property
    def blacklisted_names(self) -> typing.List[str]:
        """List of arguments names to ignore in log.

        :rtype: typing.List[str]
        """
        return self.__blacklisted_names

    @property
    def blacklisted_exceptions(self) -> typing.List[typing.Type[Exception]]:
        """List of exceptions to re-raise without log.

        :rtype: typing.List[typing.Type[Exception]]
        """
        return self.__blacklisted_exceptions

    @property
    def log_call_args(self) -> bool:
        """Flag: log call arguments before call.

        :rtype: bool
        """
        return self.__log_call_args

    @log_call_args.setter
    def log_call_args(self, val: bool) -> None:
        """Flag: log call arguments before call.

        :param val: Enable flag
        :type val: bool
        :raises TypeError: Value is not bool
        """
        if not isinstance(val, bool):
            raise TypeError("Unexpected type: {}. Should be {}.".format(val.__class__.__name__, bool.__name__))
        self.__log_call_args = val

    @property
    def log_call_args_on_exc(self) -> bool:
        """Flag: log call arguments on exception.

        :rtype: bool
        """
        return self.__log_call_args_on_exc

    @log_call_args_on_exc.setter
    def log_call_args_on_exc(self, val: bool) -> None:
        """Flag: log call arguments on exception.

        :param val: Enable flag
        :type val: bool
        :raises TypeError: Value is not bool
        """
        if not isinstance(val, bool):
            raise TypeError("Unexpected type: {}. Should be {}.".format(val.__class__.__name__, bool.__name__))
        self.__log_call_args_on_exc = val

    @property
    def log_traceback(self) -> bool:
        """Flag: log traceback on exception.

        :rtype: bool
        """
        return self.__log_traceback

    @log_traceback.setter
    def log_traceback(self, val: bool) -> None:
        """Flag: log traceback on exception.

        :param val: Enable flag
        :type val: bool
        :raises TypeError: Value is not bool
        """
        if not isinstance(val, bool):
            raise TypeError("Unexpected type: {}. Should be {}.".format(val.__class__.__name__, bool.__name__))
        self.__log_traceback = val

    @property
    def log_result_obj(self) -> bool:
        """Flag: log result object.

        :rtype: bool
        """
        return self.__log_result_obj

    @log_result_obj.setter
    def log_result_obj(self, val: bool) -> None:
        """Flag: log result object.

        :param val: Enable flag
        :type val: bool
        :raises TypeError: Value is not bool
        """
        if not isinstance(val, bool):
            raise TypeError("Unexpected type: {}. Should be {}.".format(val.__class__.__name__, bool.__name__))
        self.__log_result_obj = val

    @property
    def _logger(self) -> logging.Logger:
        """Logger instance.

        :rtype: logging.Logger
        """
        return self.__logger

    @property
    def _spec(self) -> typing.Optional[typing.Callable]:
        """Spec for function arguments.

        :rtype: typing.Callable
        """
        return self.__spec

    def __repr__(self) -> str:
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
            "log_result_obj={self.log_result_obj}, )".format(cls=self.__class__.__name__, self=self, spec=self._spec)
        )

    # noinspection PyMethodMayBeStatic
    def pre_process_param(  # pylint: disable=no-self-use
        self, arg: BoundParameter
    ) -> typing.Union[BoundParameter, typing.Tuple[BoundParameter, typing.Any], None]:
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
    def post_process_param(  # pylint: disable=unused-argument, no-self-use
        self, arg: BoundParameter, arg_repr: str
    ) -> str:
        """Process parameter for the future logging.

        :param arg: bound parameter
        :type arg: BoundParameter
        :param arg_repr: repr for value
        :type arg_repr: str
        :return: processed repr for value
        :rtype: str

        Override this method if some modifications required for result of repr() over parameter

        .. versionadded:: 3.3.0
        """
        return arg_repr

    def _get_func_args_repr(
        self, sig: inspect.Signature, args: typing.Tuple, kwargs: typing.Dict[str, typing.Any]
    ) -> str:
        """Internal helper for reducing complexity of decorator code.

        :param sig: function signature
        :type sig: inspect.Signature
        :param args: not keyworded arguments
        :type args: typing.Tuple
        :param kwargs: keyworded arguments
        :type kwargs: typing.Dict[str, typing.Any]
        :return: repr over function arguments
        :rtype: str

        .. versionchanged:: 3.3.0 Use pre- and post- processing of params during execution
        """
        if not (self.log_call_args or self.log_call_args_on_exc):
            return ""

        param_str = ""

        last_kind = None
        for param in bind_args_kwargs(sig, *args, **kwargs):
            if param.name in self.blacklisted_names:
                continue

            preprocessed = self.pre_process_param(param)
            if preprocessed is None:
                continue

            if isinstance(preprocessed, (tuple, list)):
                param, value = preprocessed
            else:
                value = param.value

            if param.empty is value:
                if param.VAR_POSITIONAL == param.kind:
                    value = ()
                elif param.VAR_KEYWORD == param.kind:
                    value = {}

            val = core.pretty_repr(src=value, indent=indent + 4, no_indent_start=True, max_indent=self.max_indent)

            val = self.post_process_param(param, val)

            if last_kind != param.kind:
                param_str += comment(kind=param.kind)
                last_kind = param.kind

            if param.empty is param.annotation:
                annotation = ""
            else:
                annotation = "  # type: {param.annotation!s}".format(param=param)

            param_str += fmt(key=param.name, annotation=annotation, val=val)
        if param_str:
            param_str += "\n"
        return param_str

    def _make_done_record(self, func_name: str, result: typing.Any) -> None:
        """Construct success record.

        :type func_name: str
        :type result: typing.Any
        """
        msg = "Done: {name!r}".format(name=func_name)

        if self.log_result_obj:
            msg += " with result:\n{result}".format(result=core.pretty_repr(result, max_indent=self.max_indent))
        self._logger.log(level=self.log_level, msg=msg)  # type: ignore

    def _make_calling_record(self, name: str, arguments: str, method: str = "Calling") -> None:
        """Make log record before execution.

        :type name: str
        :type arguments: str
        :type method: str
        """
        self._logger.log(  # type: ignore
            level=self.log_level,
            msg="{method}: \n{name!r}({arguments})".format(
                method=method, name=name, arguments=arguments if self.log_call_args else ""
            ),
        )

    def _make_exc_record(self, name: str, arguments: str) -> None:
        """Make log record if exception raised.

        :type name: str
        :type arguments: str
        """
        exc_info = sys.exc_info()
        stack = traceback.extract_stack()
        tb = traceback.extract_tb(exc_info[2])
        full_tb = stack[:2] + tb  # cut decorator and build full traceback
        exc_line = traceback.format_exception_only(*exc_info[:2])
        # Make standard traceback string
        tb_text = "Traceback (most recent call last):\n" + "".join(traceback.format_list(full_tb)) + "".join(exc_line)

        self._logger.log(  # type: ignore
            level=self.exc_level,
            msg="Failed: \n{name!r}({arguments})\n{tb_text}".format(
                name=name,
                arguments=arguments if self.log_call_args_on_exc else "",
                tb_text=tb_text if self.log_traceback else "",
            ),
            exc_info=False,
        )

    def _get_function_wrapper(self, func: typing.Callable) -> typing.Callable:
        """Here should be constructed and returned real decorator.

        :param func: Wrapped function
        :type func: typing.Callable
        :return: wrapped coroutine or function
        :rtype: typing.Callable
        """
        sig = inspect.signature(self._spec or func)

        # pylint: disable=missing-docstring
        # noinspection PyCompatibility,PyMissingOrEmptyDocstring
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):  # type: (typing.Any, typing.Any) -> typing.Any
            args_repr = self._get_func_args_repr(sig=sig, args=args, kwargs=kwargs)

            try:
                self._make_calling_record(name=func.__name__, arguments=args_repr, method="Awaiting")
                result = await func(*args, **kwargs)
                self._make_done_record(func.__name__, result)
            except BaseException as e:
                if isinstance(e, tuple(self.blacklisted_exceptions)):
                    raise
                self._make_exc_record(name=func.__name__, arguments=args_repr)
                raise
            return result

        # noinspection PyCompatibility,PyMissingOrEmptyDocstring
        @functools.wraps(func)
        def wrapper(*args, **kwargs):  # type: (typing.Any, typing.Any) -> typing.Any
            args_repr = self._get_func_args_repr(sig=sig, args=args, kwargs=kwargs)

            try:
                self._make_calling_record(name=func.__name__, arguments=args_repr)
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

    def __call__(  # pylint: disable=useless-super-delegation
        self, *args: typing.Union[typing.Callable, typing.Any], **kwargs: typing.Any
    ) -> typing.Union[typing.Callable[..., typing.Any], typing.Any]:
        """Callable instance."""
        return super(LogWrap, self).__call__(*args, **kwargs)


# pylint: enable=assigning-non-slot, abstract-method


# pylint: disable=function-redefined, unused-argument
@typing.overload
def logwrap(
    func: None = None,
    *,
    log: logging.Logger = logger,
    log_level: int = logging.DEBUG,
    exc_level: int = logging.ERROR,
    max_indent: int = 20,
    spec: typing.Optional[typing.Callable] = None,
    blacklisted_names: typing.Optional[typing.List[str]] = None,
    blacklisted_exceptions: typing.Optional[typing.List[typing.Type[Exception]]] = None,
    log_call_args: bool = True,
    log_call_args_on_exc: bool = True,
    log_traceback: bool = True,
    log_result_obj: bool = True
) -> LogWrap:
    """Overload: with no func."""
    pass  # pragma: no cover


@typing.overload  # noqa: F811
def logwrap(
    func: typing.Callable,
    *,
    log: logging.Logger = logger,
    log_level: int = logging.DEBUG,
    exc_level: int = logging.ERROR,
    max_indent: int = 20,
    spec: typing.Optional[typing.Callable] = None,
    blacklisted_names: typing.Optional[typing.List[str]] = None,
    blacklisted_exceptions: typing.Optional[typing.List[typing.Type[Exception]]] = None,
    log_call_args: bool = True,
    log_call_args_on_exc: bool = True,
    log_traceback: bool = True,
    log_result_obj: bool = True
) -> typing.Callable:
    """Overload: func provided."""
    pass  # pragma: no cover


# pylint: enable=unused-argument
def logwrap(  # noqa: F811  # pylint: disable=unexpected-keyword-arg, no-value-for-parameter
    func: typing.Optional[typing.Callable] = None,
    *,
    log: logging.Logger = logger,
    log_level: int = logging.DEBUG,
    exc_level: int = logging.ERROR,
    max_indent: int = 20,
    spec: typing.Optional[typing.Callable] = None,
    blacklisted_names: typing.Optional[typing.Iterable[str]] = None,
    blacklisted_exceptions: typing.Optional[typing.Iterable[typing.Type[Exception]]] = None,
    log_call_args: bool = True,
    log_call_args_on_exc: bool = True,
    log_traceback: bool = True,
    log_result_obj: bool = True
) -> typing.Union[LogWrap, typing.Callable]:
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
                 Note: this object should provide fully compatible signature
                 with decorated function, or arguments bind will be failed!
    :type spec: typing.Optional[typing.Callable]
    :param blacklisted_names: Blacklisted argument names. Arguments with this names will be skipped in log.
    :type blacklisted_names: typing.Optional[typing.Iterable[str]]
    :param blacklisted_exceptions: list of exceptions, which should be re-raised without producing log record.
    :type blacklisted_exceptions: typing.Optional[typing.Iterable[typing.Type[Exception]]]
    :param log_call_args: log call arguments before executing wrapped function.
    :type log_call_args: bool
    :param log_call_args_on_exc: log call arguments if exception raised.
    :type log_call_args_on_exc: bool
    :param log_traceback: log traceback on excaption in addition to failure info
    :type log_traceback: bool
    :param log_result_obj: log result of function call.
    :type log_result_obj: bool
    :return: built real decorator.
    :rtype: _log_wrap_shared.BaseLogWrap

    .. versionchanged:: 3.3.0 Extract func from log and do not use Union.
    .. versionchanged:: 3.3.0 Deprecation of *args
    .. versionchanged:: 4.0.0 Drop of *args
    .. versionchanged:: 5.1.0 log_traceback parameter
    """
    wrapper = LogWrap(
        log=log,
        log_level=log_level,
        exc_level=exc_level,
        max_indent=max_indent,
        spec=spec,
        blacklisted_names=blacklisted_names,
        blacklisted_exceptions=blacklisted_exceptions,
        log_call_args=log_call_args,
        log_call_args_on_exc=log_call_args_on_exc,
        log_traceback=log_traceback,
        log_result_obj=log_result_obj,
    )
    if func is not None:
        return wrapper(func)
    return wrapper


# pylint: enable=function-redefined
