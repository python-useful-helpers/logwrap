#    Copyright 2016 - 2022 Alexey Stepanov aka penguinolog

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

from __future__ import annotations

# Standard Library
import asyncio
import functools
import inspect
import logging
import os
import sys
import traceback
import types
import typing

# Package Implementation
from logwrap import constants
from logwrap import repr_utils

if typing.TYPE_CHECKING:
    # Standard Library
    from collections.abc import Iterable
    from collections.abc import MutableMapping

__all__ = ("LogWrap", "logwrap", "BoundParameter", "bind_args_kwargs")

LOGGER: logging.Logger = logging.getLogger("logwrap")
INDENT = 4
_CURRENT_FILE = os.path.abspath(__file__)

_WrappedT = typing.TypeVar("_WrappedT", bound=typing.Callable[..., typing.Any])


class BoundParameter(inspect.Parameter):
    """Parameter-like object store BOUND with value parameter.

    .. versionadded:: 3.3.0
    .. versionchanged:: 5.3.1 subclass inspect.Parameter
    """

    __slots__ = ("_value",)

    def __init__(
        self,
        parameter: inspect.Parameter,
        value: typing.Any = inspect.Parameter.empty,
    ) -> None:
        """Parameter-like object store BOUND with value parameter.

        :param parameter: parameter from signature
        :type parameter: inspect.Parameter
        :param value: parameter real value
        :type value: typing.Any
        :raises ValueError: No default value and no value
        """
        super().__init__(
            name=parameter.name,
            kind=parameter.kind,
            default=parameter.default,
            annotation=parameter.annotation,
        )

        if value is self.empty:
            if parameter.default is self.empty and parameter.kind not in (self.VAR_POSITIONAL, self.VAR_KEYWORD):
                raise ValueError("Value is not set and no default value")
            self._value: typing.Any = parameter.default
        else:
            self._value = value

    @property
    def value(self) -> typing.Any:
        """Parameter value.

        :return: actual parameter value
        :rtype: typing.Any
        """
        return self._value

    def __str__(self) -> str:
        """Debug purposes.

        :return: string representation for parameter. */** flags is attached if positional (*args) or keyword (**kwargs)
        :rtype: str
        """
        # POSITIONAL_ONLY is only in precompiled functions or Python 3.8+
        if self.kind == self.POSITIONAL_ONLY:  # pragma: no cover
            as_str: str = "" if self.name is None else f"<{self.name}>"
        else:
            as_str = self.name or ""

        # Add annotation if applicable (python 3 only)
        if self.annotation is not self.empty:
            as_str += f": {inspect.formatannotation(self.annotation)!s}"

        value = self.value
        if value is self.empty:
            if self.VAR_POSITIONAL == self.kind:
                value = ()
            elif self.VAR_KEYWORD == self.kind:
                value = {}

        as_str += f"={value!r}"

        if self.default is not self.empty:
            as_str += f"  # {self.default!r}"

        if self.kind == self.VAR_POSITIONAL:
            as_str = "*" + as_str
        elif self.kind == self.VAR_KEYWORD:
            as_str = "**" + as_str

        return as_str

    def __repr__(self) -> str:
        """Debug purposes.

        :return: representation for logging/debug purposes
        :rtype: str
        """
        return f'<{self.__class__.__name__} "{self}">'


def bind_args_kwargs(
    sig: inspect.Signature,
    *args: typing.Any,
    **kwargs: typing.Any,
) -> list[BoundParameter]:
    """Bind *args and **kwargs to signature and get Bound Parameters.

    :param sig: source signature
    :type sig: inspect.Signature
    :param args: positional arguments
    :type args: typing.Any
    :param kwargs: keyword arguments
    :type kwargs: typing.Any
    :return: Iterator for bound parameters with all information about it
    :rtype: typing.List[BoundParameter]

    .. versionadded:: 3.3.0
    .. versionchanged:: 5.3.1 return list
    """
    result: list[BoundParameter] = []
    bound: MutableMapping[str, inspect.Parameter] = sig.bind(*args, **kwargs).arguments
    for param in sig.parameters.values():
        result.append(BoundParameter(parameter=param, value=bound.get(param.name, param.default)))
    return result


class LogWrap:
    """Base class for LogWrap implementation."""

    __slots__ = (
        "__blacklisted_names",
        "__blacklisted_exceptions",
        "__logger",
        "__log_level",
        "__exc_level",
        "__max_indent",
        "__log_call_args",
        "__log_call_args_on_exc",
        "__log_traceback",
        "__log_result_obj",
    )

    def __init__(
        self,
        log: logging.Logger | None = None,
        log_level: int = logging.DEBUG,
        exc_level: int = logging.ERROR,
        max_indent: int = 20,
        blacklisted_names: Iterable[str] | None = None,
        blacklisted_exceptions: Iterable[type[Exception]] | None = None,
        log_call_args: bool = True,
        log_call_args_on_exc: bool = True,
        log_traceback: bool = True,
        log_result_obj: bool = True,
    ) -> None:
        """Log function calls and return values.

        :param log: logger object for decorator, by default trying to use logger from target module. Fallback: 'logwrap'
        :type log: typing.Optional[logging.Logger]
        :param log_level: log level for successful calls
        :type log_level: int
        :param exc_level: log level for exception cases
        :type exc_level: int
        :param max_indent: maximum indent before classic `repr()` call.
        :type max_indent: int
        :param blacklisted_names: Blacklisted argument names. Arguments with this names will be skipped in log.
        :type blacklisted_names: Iterable[str] | None
        :param blacklisted_exceptions: list of exception, which should be re-raised
               without producing traceback and text log record.
        :type blacklisted_exceptions: Iterable[type[Exception]]
        :param log_call_args: log call arguments before executing wrapped function.
        :type log_call_args: bool
        :param log_call_args_on_exc: log call arguments if exception raised.
        :type log_call_args_on_exc: bool
        :param log_traceback: log traceback on exception in addition to failure info
        :type log_traceback: bool
        :param log_result_obj: log result of function call.
        :type log_result_obj: bool

        .. versionchanged:: 3.3.0 Extract func from log and do not use Union.
        .. versionchanged:: 5.1.0 log_traceback parameter
        .. versionchanged:: 8.0.0 pick up logger from target module if possible
        .. versionchanged:: 9.0.0 Only LogWrap instance act as decorator
        """
        # Typing fix:
        if blacklisted_names is None:
            self.__blacklisted_names: list[str] = []
        else:
            self.__blacklisted_names = list(blacklisted_names)
        if blacklisted_exceptions is None:
            self.__blacklisted_exceptions: list[type[Exception]] = []
        else:
            self.__blacklisted_exceptions = list(blacklisted_exceptions)

        if isinstance(log, logging.Logger):
            self.__logger: logging.Logger | None = log
        else:
            self.__logger = None

        self.__log_level: int = log_level
        self.__exc_level: int = exc_level
        self.__max_indent: int = max_indent
        self.__log_call_args: bool = log_call_args
        self.__log_call_args_on_exc: bool = log_call_args_on_exc
        self.__log_traceback: bool = log_traceback
        self.__log_result_obj: bool = log_result_obj

        # We are not interested to pass any arguments to object

    def _get_logger_for_func(self, func: _WrappedT) -> logging.Logger:
        """Get logger for function from function module if possible.

        :param func: decorated function
        :type func: FuncResultType
        :return: logger instance
        :rtype: logging.Logger
        """
        if self.__logger is not None:
            return self.__logger

        func_module = inspect.getmodule(func)
        for logger_name in constants.VALID_LOGGER_NAMES:
            logger_candidate = getattr(func_module, logger_name, None)
            if isinstance(logger_candidate, logging.Logger):
                return logger_candidate
        return LOGGER

    @property
    def log_level(self) -> int:
        """Log level for normal behavior.

        :return: log level for normal behavior
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
            raise TypeError(f"Unexpected type: {val.__class__.__name__}. Should be {int.__name__}.")
        self.__log_level = val

    @property
    def exc_level(self) -> int:
        """Log level for exceptions.

        :return: log level for exceptions cases
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
            raise TypeError(f"Unexpected type: {val.__class__.__name__}. Should be {int.__name__}.")
        self.__exc_level = val

    @property
    def max_indent(self) -> int:
        """Maximum indentation.

        :return: maximum allowed indentation before switch to normal repr
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
            raise TypeError(f"Unexpected type: {val.__class__.__name__}. Should be {int.__name__}.")
        self.__max_indent = val

    @property
    def blacklisted_names(self) -> list[str]:
        """List of arguments names to ignore in log.

        :return: list of arguments to ignore in log
        :rtype: typing.List[str]
        """
        return self.__blacklisted_names

    @property
    def blacklisted_exceptions(self) -> list[type[Exception]]:
        """List of exceptions to re-raise without log traceback and text.

        :return: list of exceptions to re-raise silent
        :rtype: typing.List[typing.Type[Exception]]
        """
        return self.__blacklisted_exceptions

    @property
    def log_call_args(self) -> bool:
        """Flag: log call arguments before call.

        :return: log cal arguments before call
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
            raise TypeError(f"Unexpected type: {val.__class__.__name__}. Should be {bool.__name__}.")
        self.__log_call_args = val

    @property
    def log_call_args_on_exc(self) -> bool:
        """Flag: log call arguments on exception.

        :return: log call arguments in case of exception logging
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
            raise TypeError(f"Unexpected type: {val.__class__.__name__}. Should be {bool.__name__}.")
        self.__log_call_args_on_exc = val

    @property
    def log_traceback(self) -> bool:
        """Flag: log traceback on exception.

        :return: log traceback in case of exception logging
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
            raise TypeError(f"Unexpected type: {val.__class__.__name__}. Should be {bool.__name__}.")
        self.__log_traceback = val

    @property
    def log_result_obj(self) -> bool:
        """Flag: log result object.

        :return: log execution result object
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
            raise TypeError(f"Unexpected type: {val.__class__.__name__}. Should be {bool.__name__}.")
        self.__log_result_obj = val

    @property
    def _logger(self) -> logging.Logger | None:
        """Logger instance.

        :return: logger instance if configured
        :rtype: typing.Optional[logging.Logger]
        """
        return self.__logger

    def __repr__(self) -> str:
        """Repr for debug purposes.

        :return: representation for logging/debug purposes
        :rtype: str
        """
        return (
            f"{self.__class__.__name__}("
            f"log={self._logger}, "
            f"log_level={self.log_level}, "
            f"exc_level={self.exc_level}, "
            f"max_indent={self.max_indent}, "
            f"blacklisted_names={self.blacklisted_names}, "
            f"blacklisted_exceptions={self.blacklisted_exceptions}, "
            f"log_call_args={self.log_call_args}, "
            f"log_call_args_on_exc={self.log_call_args_on_exc}, "
            f"log_result_obj={self.log_result_obj}, )"
        )

    # noinspection PyMethodMayBeStatic
    def pre_process_param(
        self,
        arg: BoundParameter,
    ) -> BoundParameter | tuple[BoundParameter, typing.Any] | None:
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
    def post_process_param(  # pylint: disable=unused-argument
        self,
        arg: BoundParameter,  # NOSONAR
        arg_repr: str,
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

    def _safe_val_repr(self, value: typing.Any) -> str:
        """Try to get repr for value and provide fallback text in case of impossibility.

        :param value: value to try make repr
        :type value: typing.Any
        :return: repr string or fallback description
        :rtype: str
        """
        try:
            return repr_utils.pretty_repr(
                src=value,
                indent=INDENT + 4,
                no_indent_start=True,
                max_indent=self.max_indent,
            )
        except Exception as exc:
            base_name: str = getattr(value, "name", getattr(value, "__name__", value.__class__.__name__))
            base_details: str = f"at 0x{id(value):X} (repr failed with reason: {exc})"
            if isinstance(value, types.FunctionType):  # pragma: no cover
                return f"<function {base_name} {base_details}>"
            if isinstance(value, types.MethodType):  # pragma: no cover
                return f"<method {base_name} {base_details}>"
            return f"<object {base_name} {base_details}>"

    def _get_func_args_repr(
        self,
        sig: inspect.Signature,
        args: tuple[typing.Any, ...],
        kwargs: dict[str, typing.Any],
    ) -> str:
        """Internal helper for reducing complexity of decorator code.

        :param sig: function signature
        :type sig: inspect.Signature
        :param args: positional arguments
        :type args: typing.Tuple
        :param kwargs: keyword arguments
        :type kwargs: typing.Dict[str, typing.Any]
        :return: repr over function arguments
        :rtype: str

        .. versionchanged:: 3.3.0 Use pre- and post- processing of params during execution
        """
        if not (self.log_call_args or self.log_call_args_on_exc):
            return ""

        param_str: str = ""

        last_kind = None
        for param in bind_args_kwargs(sig, *args, **kwargs):
            if param.name in self.blacklisted_names:
                continue

            preprocessed: (BoundParameter | tuple[BoundParameter, typing.Any] | None) = self.pre_process_param(param)
            if preprocessed is None:
                continue

            if isinstance(preprocessed, (tuple, list)):
                param, value = preprocessed
            else:
                value = param.value

            if value is param.empty:
                if param.VAR_POSITIONAL == param.kind:
                    value = ()
                elif param.VAR_KEYWORD == param.kind:
                    value = {}

            val: str = self._safe_val_repr(value)

            val = self.post_process_param(param, val)

            if last_kind != param.kind:
                param_str += f"\n{'':<{INDENT}}# {param.kind!s}:"
                last_kind = param.kind

            if param.annotation is param.empty:
                annotation: str = ""
            else:
                annotation = f"  # type: {getattr(param.annotation, '__name__', param.annotation)!s}"

            param_str += f"\n{'':<{INDENT}}{param.name}={val},{annotation}"
        if param_str:
            param_str += "\n"
        return param_str

    def _make_done_record(self, logger: logging.Logger, func_name: str, result: typing.Any) -> None:
        """Construct success record.

        :param logger: logger instance to use
        :type logger: logging.Logger
        :param func_name: function name
        :type func_name: str
        :param result: function execution result
        :type result: typing.Any
        """
        msg: str = f"Done: {func_name!r}"

        if self.log_result_obj:
            msg += f" with result:\n{repr_utils.pretty_repr(result, max_indent=self.max_indent)}"
        logger.log(level=self.log_level, msg=msg)

    def _make_calling_record(self, logger: logging.Logger, name: str, arguments: str, method: str = "Calling") -> None:
        """Make log record before execution.

        :param logger: logger instance to use
        :type logger: logging.Logger
        :param name: function name
        :type name: str
        :param arguments: function arguments repr
        :type arguments: str
        :param method: "calling" or "awaiting"
        :type method: str
        """
        logger.log(level=self.log_level, msg=f"{method}: \n{name}({arguments if self.log_call_args else ''})")

    def _make_exc_record(self, logger: logging.Logger, name: str, arguments: str, exception: Exception) -> None:
        """Make log record if exception raised.

        :param logger: logger instance to use
        :type logger: logging.Logger
        :param name: function name
        :type name: str
        :param arguments: function arguments repr
        :type arguments: str
        :param exception: exception captured
        :type exception: Exception
        """
        exc_info = sys.exc_info()
        stack: traceback.StackSummary = traceback.extract_stack()
        full_tb: list[traceback.FrameSummary] = [elem for elem in stack if elem.filename != _CURRENT_FILE]
        exc_line: list[str] = traceback.format_exception_only(*exc_info[:2])
        # Make standard traceback string
        tb_text: str = (
            f"Traceback (most recent call last):\n{''.join(traceback.format_list(full_tb))}{''.join(exc_line)}"
            if self.log_traceback and not isinstance(exception, tuple(self.blacklisted_exceptions))
            else exception.__class__.__name__
        )

        logger.log(
            level=self.exc_level,
            msg=f"Failed: \n{name}({arguments if self.log_call_args_on_exc else ''})\n{tb_text}",
            exc_info=False,
        )

    def _get_function_wrapper(self, func: _WrappedT) -> _WrappedT:
        """Here should be constructed and returned real decorator.

        :param func: Wrapped function
        :type func: typing.Callable
        :return: wrapped coroutine or function
        :rtype: typing.Callable
        """

        logger: logging.Logger = self._get_logger_for_func(func)

        @functools.wraps(func)
        async def async_wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            """Decorator for async callable objects.

            :return: function result
            :rtype: typing.Any
            :raises Exception: something went wrong. Exception has been logged if not blacklisted/disabled log.
            """
            sig: inspect.Signature = inspect.signature(func)
            args_repr: str = self._get_func_args_repr(sig=sig, args=args, kwargs=kwargs)

            try:
                self._make_calling_record(logger=logger, name=func.__name__, arguments=args_repr, method="Awaiting")
                result = await func(*args, **kwargs)
                self._make_done_record(logger=logger, func_name=func.__name__, result=result)
            except Exception as e:
                self._make_exc_record(logger=logger, name=func.__name__, arguments=args_repr, exception=e)
                raise
            return result

        @functools.wraps(func)
        def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            """Decorator for normal callable objects.

            :return: function result
            :rtype: typing.Any
            :raises Exception: something went wrong. Exception has been logged if not blacklisted/disabled log.
            """
            sig: inspect.Signature = inspect.signature(func)
            args_repr: str = self._get_func_args_repr(sig=sig, args=args, kwargs=kwargs)

            try:
                self._make_calling_record(logger=logger, name=func.__name__, arguments=args_repr)
                result = func(*args, **kwargs)
                self._make_done_record(logger=logger, func_name=func.__name__, result=result)
            except Exception as e:
                self._make_exc_record(logger=logger, name=func.__name__, arguments=args_repr, exception=e)
                raise
            return result

        return async_wrapper if asyncio.iscoroutinefunction(func) else wrapper  # type: ignore[return-value]

    def __call__(self, func: _WrappedT) -> _WrappedT:
        """Callable instance.

        :return: decorated function
        :rtype: typing.Callable[..., FuncResultType]
        """
        return self._get_function_wrapper(func)


@typing.overload
def logwrap(
    *,
    log: logging.Logger | None = None,
    log_level: int = logging.DEBUG,
    exc_level: int = logging.ERROR,
    max_indent: int = 20,
    blacklisted_names: Iterable[str] | None = None,
    blacklisted_exceptions: Iterable[type[Exception]] | None = None,
    log_call_args: bool = True,
    log_call_args_on_exc: bool = True,
    log_traceback: bool = True,
    log_result_obj: bool = True,
) -> LogWrap:
    """Overload: with no func."""


@typing.overload
def logwrap(
    func: None = None,
    /,
    *,
    log: logging.Logger | None = None,
    log_level: int = logging.DEBUG,
    exc_level: int = logging.ERROR,
    max_indent: int = 20,
    blacklisted_names: Iterable[str] | None = None,
    blacklisted_exceptions: Iterable[type[Exception]] | None = None,
    log_call_args: bool = True,
    log_call_args_on_exc: bool = True,
    log_traceback: bool = True,
    log_result_obj: bool = True,
) -> LogWrap:
    """Overload: with no func."""


@typing.overload
def logwrap(
    func: _WrappedT,
    /,
    *,
    log: logging.Logger | None = None,
    log_level: int = logging.DEBUG,
    exc_level: int = logging.ERROR,
    max_indent: int = 20,
    blacklisted_names: Iterable[str] | None = None,
    blacklisted_exceptions: Iterable[type[Exception]] | None = None,
    log_call_args: bool = True,
    log_call_args_on_exc: bool = True,
    log_traceback: bool = True,
    log_result_obj: bool = True,
) -> _WrappedT:
    """Overload: func provided."""


def logwrap(  # pylint: disable=differing-param-doc,differing-type-doc
    func: _WrappedT | None = None,
    /,
    *,
    log: logging.Logger | None = None,
    log_level: int = logging.DEBUG,
    exc_level: int = logging.ERROR,
    max_indent: int = 20,
    blacklisted_names: Iterable[str] | None = None,
    blacklisted_exceptions: Iterable[type[Exception]] | None = None,
    log_call_args: bool = True,
    log_call_args_on_exc: bool = True,
    log_traceback: bool = True,
    log_result_obj: bool = True,
) -> LogWrap | _WrappedT:
    """Log function calls and return values.

    :param func: function to wrap
    :type func: typing.Optional[typing.Callable]
    :param log: logger object for decorator, by default trying to use logger from target module. Fallback: 'logwrap'
    :type log: typing.Optional[logging.Logger]
    :param log_level: log level for successful calls
    :type log_level: int
    :param exc_level: log level for exception cases
    :type exc_level: int
    :param max_indent: maximum indent before classic `repr()` call.
    :type max_indent: int
    :param blacklisted_names: Blacklisted argument names. Arguments with this names will be skipped in log.
    :type blacklisted_names: Iterable[str] | None
    :param blacklisted_exceptions: list of exceptions, which should be re-raised
                                   without producing traceback and text log record.
    :type blacklisted_exceptions: Iterable[type[Exception]] | None
    :param log_call_args: log call arguments before executing wrapped function.
    :type log_call_args: bool
    :param log_call_args_on_exc: log call arguments if exception raised.
    :type log_call_args_on_exc: bool
    :param log_traceback: log traceback on exception in addition to failure info
    :type log_traceback: bool
    :param log_result_obj: log result of function call.
    :type log_result_obj: bool
    :return: built real decorator.
    :rtype: typing.Union[LogWrap, typing.Callable[..., FuncResultType]]

    .. versionchanged:: 3.3.0 Extract func from log and do not use Union.
    .. versionchanged:: 3.3.0 Deprecation of *args
    .. versionchanged:: 4.0.0 Drop of *args
    .. versionchanged:: 5.1.0 log_traceback parameter
    .. versionchanged:: 8.0.0 pick up logger from target module if possible
    .. versionchanged:: 9.0.0 Only LogWrap instance act as decorator
    """
    wrapper = LogWrap(
        log=log,
        log_level=log_level,
        exc_level=exc_level,
        max_indent=max_indent,
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
