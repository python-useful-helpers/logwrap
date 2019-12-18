.. logwrap function and LogWrap class description.

API: Decorators: `LogWrap` class and `logwrap` function.
========================================================

.. py:module:: logwrap
.. py:currentmodule:: logwrap

.. py:class:: LogWrap(object)

    Log function calls and return values.

    .. versionadded:: 2.2.0

    .. py:method:: __init__(func=None, *, log=None, log_level=logging.DEBUG, exc_level=logging.ERROR, max_indent=20, spec=None, blacklisted_names=None, blacklisted_exceptions=None, log_call_args=True, log_call_args_on_exc=True, log_traceback=True, log_result_obj=True, )

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
        :param spec: callable object used as spec for arguments bind.
                     This is designed for the special cases only,
                     when impossible to change signature of target object,
                     but processed/redirected signature is accessible.
                     Note: this object should provide fully compatible
                     signature with decorated function, or arguments bind
                     will be failed!
        :type spec: typing.Optional[typing.Callable]
        :param blacklisted_names: Blacklisted argument names.
                                  Arguments with this names will be skipped in log.
        :type blacklisted_names: typing.Optional[typing.Iterable[str]]
        :param blacklisted_exceptions: list of exception,
                                       which should be re-raised without
                                       producing traceback and text log record.
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
        .. versionchanged:: 3.3.0 Deprecation of `*args`
        .. versionchanged:: 4.0.0 Drop of `*args`
        .. versionchanged:: 5.1.0 log_traceback parameter
        .. versionchanged:: 8.0.0 pick up logger from target module if possible

    .. py:method:: pre_process_param(self, arg)

        Process parameter for the future logging.

        :param arg: bound parameter
        :type arg: BoundParameter
        :return: value, value override for logging or None if argument should not be logged.
        :rtype: typing.Union[BoundParameter, typing.Tuple[BoundParameter, typing.Any], None]

        Override this method if some modifications required for parameter value before logging

        .. versionadded:: 3.3.0

    .. py:method:: post_process_param(self, arg, arg_repr)

        Process parameter for the future logging.

        :param arg: bound parameter
        :type arg: BoundParameter
        :param arg_repr: repr for value
        :type arg_repr: typing.Text
        :return: processed repr for value
        :rtype: typing.Text

        Override this method if some modifications required for result of repr() over parameter

        .. versionadded:: 3.3.0

    .. note:: Attributes/properties names the same as argument names and changes
              the same fields.

    .. py:attribute:: log_level
    .. py:attribute:: exc_level
    .. py:attribute:: max_indent
    .. py:attribute:: blacklisted_names

        ``typing.List[str]``, modified via mutability
    .. py:attribute:: blacklisted_exceptions

        ``typing.List[typing.Type[Exception]]``, modified via mutability
    .. py:attribute:: log_call_args
    .. py:attribute:: log_call_args_on_exc
    .. py:attribute:: log_traceback
    .. py:attribute:: log_result_obj

    .. py:attribute:: _func

        ``typing.Optional[typing.Callable[..., typing.Awaitable]]``
        Wrapped function. Used for inheritance only.

    .. py:method:: __call__(*args, **kwargs)

        Decorator entry-point. Logic is stored separately and load depends on python version.

        :return: Decorated function. On python 3.3+ awaitable is supported.
        :rtype: typing.Union[typing.Callable, typing.Awaitable]


.. py:function:: logwrap(func=None, *, log=None, log_level=logging.DEBUG, exc_level=logging.ERROR, max_indent=20, spec=None, blacklisted_names=None, blacklisted_exceptions=None, log_call_args=True, log_call_args_on_exc=True, log_traceback=True, log_result_obj=True, )

    Log function calls and return values.

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
    :param spec: callable object used as spec for arguments bind.
                 This is designed for the special cases only,
                 when impossible to change signature of target object,
                 but processed/redirected signature is accessible.
                 Note: this object should provide fully compatible signature
                 with decorated function, or arguments bind will be failed!
    :type spec: typing.Optional[typing.Callable]
    :param blacklisted_names: Blacklisted argument names. Arguments with this names will be skipped in log.
    :type blacklisted_names: typing.Optional[typing.Iterable[str]]
    :param blacklisted_exceptions: list of exceptions, which should be re-raised
                                   without producing traceback and text log record.
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
    :rtype: typing.Union[LogWrap, typing.Callable[..., typing.Union[typing.Awaitable[typing.Any], typing.Any]]]

    .. versionchanged:: 3.3.0 Extract func from log and do not use Union.
    .. versionchanged:: 3.3.0 Deprecation of *args
    .. versionchanged:: 4.0.0 Drop of *args
    .. versionchanged:: 5.1.0 log_traceback parameter
    .. versionchanged:: 8.0.0 pick up logger from target module if possible


.. py:class:: BoundParameter(inspect.Parameter)

    Parameter-like object store BOUND with value parameter.
    .. versionchanged:: 5.3.1 subclass inspect.Parameter

    .. versionadded:: 3.3.0

    .. py:method:: __init__(self, parameter, value=Parameter.empty)

        Parameter-like object store BOUND with value parameter.

        :param parameter: parameter from signature
        :type parameter: ``inspect.Parameter``
        :param value: parameter real value
        :type value: typing.Any
        :raises ValueError: No default value and no value

    .. py:attribute:: parameter

        Parameter object.

        :rtype: BoundParameter

    .. py:attribute:: value

        Parameter value.

        :rtype: typing.Any

    .. py:method:: __str__(self)

        String representation.

        :rtype: ``str``


.. py:function:: bind_args_kwargs(sig, *args, **kwargs)

    Bind `*args` and `**kwargs` to signature and get Bound Parameters.

    :param sig: source signature
    :type sig: inspect.Signature
    :return: Iterator for bound parameters with all information about it
    :rtype: typing.List[BoundParameter]

    .. versionadded:: 3.3.0
    .. versionchanged:: 5.3.1 return list
