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

cpdef tuple __all__ = ("LogWrap", "logwrap", "BoundParameter", "bind_args_kwargs")

import asyncio
import functools
import inspect
import logging
import sys
import traceback
import typing
import warnings

from logwrap cimport repr_utils
from logwrap cimport class_decorator


logger = logging.getLogger("logwrap")  # type: logging.Logger


cdef unsigned long indent = 4
fmt = "\n{spc:<{indent}}{{key!r}}={{val}},{{annotation}}".format(spc="", indent=indent).format
comment = "\n{spc:<{indent}}# {{kind!s}}:".format(spc="", indent=indent).format


class BoundParameter(inspect.Parameter):
    """Parameter-like object store BOUND with value parameter.

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
            name=parameter.name,
            kind=parameter.kind,
            default=parameter.default,
            annotation=parameter.annotation
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
        cdef str as_str

        # POSITIONAL_ONLY is only in precompiled functions
        if self.kind == self.POSITIONAL_ONLY:
            as_str = "" if self.name is None else "<{as_str}>".format(as_str=self.name)
        else:
            as_str = self.name or ""

        # Add annotation if applicable (python 3 only)
        if self.annotation is not self.empty:
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


def bind_args_kwargs(sig: inspect.Signature, *args: typing.Any, **kwargs: typing.Any) ->typing.List[BoundParameter]:
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
    .. versionchanged:: 5.3.1 cythonize and return list
    """
    cdef list result = []

    bound = sig.bind(*args, **kwargs).arguments
    for param in sig.parameters.values():
        result.append(BoundParameter(parameter=param, value=bound.get(param.name, param.default)))
    return result


cdef class LogWrap(class_decorator.BaseDecorator):
    """Base class for LogWrap implementation."""

    def __init__(
        self,
        func: typing.Optional[typing.Callable[..., typing.Union[typing.Awaitable[typing.Any], typing.Any]]] = None,
        *,
        log: logging.Logger = logger,
        unsigned long log_level=logging.DEBUG,
        unsigned long exc_level=logging.ERROR,
        unsigned long max_indent=20,
        spec: typing.Optional[typing.Callable[..., typing.Any]] = None,
        blacklisted_names: typing.Optional[typing.Iterable[str]] = None,
        blacklisted_exceptions: typing.Optional[typing.Iterable[typing.Type[Exception]]] = None,
        bint log_call_args=True,
        bint log_call_args_on_exc=True,
        bint log_traceback=True,
        bint log_result_obj=True
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

        self.log_level = log_level
        self.exc_level = exc_level
        self.max_indent = max_indent

        self.log_call_args = log_call_args
        self.log_call_args_on_exc = log_call_args_on_exc
        self.log_traceback = log_traceback
        self.log_result_obj = log_result_obj

        # Typing fix:
        if blacklisted_names is None:
            self.__blacklisted_names = []  # type: typing.List[str]
        else:
            self.__blacklisted_names = list(blacklisted_names)
        if blacklisted_exceptions is None:
            self.__blacklisted_exceptions = []  # type: typing.List[typing.Type[Exception]]
        else:
            self.__blacklisted_exceptions = list(blacklisted_exceptions)

        self._logger = log
        self._spec = spec or self._func

        # We are not interested to pass any arguments to object

    @property
    def blacklisted_names(self) -> typing.List[str]:
        """List of arguments names to ignore in log."""
        return self.__blacklisted_names

    @property
    def blacklisted_exceptions(self) -> typing.List[typing.Type[Exception]]:
        """List of exceptions to re-raise without log."""
        return self.__blacklisted_exceptions

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

    cpdef object pre_process_param(self, object arg: BoundParameter):
        """Process parameter for the future logging.

        :param arg: bound parameter
        :type arg: BoundParameter
        :return: value, value override for logging or None if argument should not be logged.
        :rtype: typing.Union[BoundParameter, typing.Tuple[BoundParameter, typing.Any], None]

        Override this method if some modifications required for parameter value before logging

        .. versionadded:: 3.3.0
        """
        return arg

    cpdef str post_process_param(self, object arg: BoundParameter, str arg_repr):
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

    cdef:
        str _get_func_args_repr(self, sig: inspect.Signature, tuple args: typing.Tuple[typing.Any, ...], dict kwargs: typing.Dict[str, typing.Any]):
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

            cdef:
                str param_str = ""
                str val
                str annotation

            last_kind = None
            for param in bind_args_kwargs(sig, *args, **kwargs):  # type: BoundParameter
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

                val = repr_utils.pretty_repr(src=value, indent=indent + 4, no_indent_start=True, max_indent=self.max_indent)

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

        void _make_done_record(self, str func_name, result: typing.Any) except *:
            """Construct success record.
    
            :type func_name: str
            :type result: typing.Any
            """
            cdef str msg = "Done: {name!r}".format(name=func_name)

            if self.log_result_obj:
                msg += " with result:\n{result}".format(
                    result=repr_utils.pretty_repr(
                        result,
                        indent=0,
                        no_indent_start=False,
                        max_indent=self.max_indent,
                        indent_step=4

                    )
                )
            self._logger.log(level=self.log_level, msg=msg)  # type: ignore

        void _make_calling_record(self, str name, str arguments, str method="Calling") except *:
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

        void _make_exc_record(self, str name, str arguments) except *:
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
            cdef str tb_text = "Traceback (most recent call last):\n" + "".join(traceback.format_list(full_tb)) + "".join(exc_line)

            self._logger.log(  # type: ignore
                level=self.exc_level,
                msg="Failed: \n{name!r}({arguments})\n{tb_text}".format(
                    name=name,
                    arguments=arguments if self.log_call_args_on_exc else "",
                    tb_text=tb_text if self.log_traceback else "",
                ),
                exc_info=False,
            )

    def _get_function_wrapper(
        self, func: typing.Callable[..., typing.Union[typing.Awaitable[typing.Any], typing.Any]]
    ) -> typing.Callable[..., typing.Union[typing.Awaitable[typing.Any], typing.Any]]:
        """Here should be constructed and returned real decorator.

        :param func: Wrapped function
        :type func: typing.Callable
        :return: wrapped coroutine or function
        :rtype: typing.Callable
        """
        sig = inspect.signature(self._spec or func)

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

        return async_wrapper if asyncio.iscoroutinefunction(func) else wrapper

    def __call__(
        self,
        *args: typing.Union[typing.Callable[..., typing.Union[typing.Awaitable[typing.Any], typing.Any]], typing.Any],
        **kwargs: typing.Any,
    ) -> typing.Union[typing.Callable[..., typing.Union[typing.Awaitable[typing.Any], typing.Any]], typing.Any]:
        """Callable instance."""
        return super(LogWrap, self).__call__(*args, **kwargs)


def logwrap(
    func: typing.Optional[typing.Callable[..., typing.Union[typing.Awaitable[typing.Any], typing.Any]]] = None,
    *,
    log: logging.Logger = logger,
    unsigned long log_level=logging.DEBUG,
    unsigned long exc_level=logging.ERROR,
    unsigned long max_indent=20,
    spec: typing.Optional[typing.Callable[..., typing.Any]] = None,
    blacklisted_names: typing.Optional[typing.Iterable[str]] = None,
    blacklisted_exceptions: typing.Optional[typing.Iterable[typing.Type[Exception]]] = None,
    bint log_call_args=True,
    bint log_call_args_on_exc=True,
    bint log_traceback=True,
    bint log_result_obj=True
) -> typing.Union[LogWrap, typing.Callable[..., typing.Union[typing.Awaitable[typing.Any], typing.Any]]]:
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
