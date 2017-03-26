.. logwrap function and LogWrap class description.

API: Decorators: `LogWrap` class and `logwrap` function.
========================================================

.. py:module:: logwrap
.. py:currentmodule:: logwrap

.. py:class:: LogWrap(log=logging.getLogger('logwrap'), log_level=logging.DEBUG, exc_level=logging.ERROR, max_indent=20, spec=None, blacklisted_names=None, blacklisted_exceptions=None, log_call_args=True, log_call_args_on_exc=True, log_result_obj=True, )

    Log function calls and return values.

    .. versionadded:: 2.2.0

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
    :type spec: callable
    :param blacklisted_names: Blacklisted argument names.
                              Arguments with this names will be skipped in log.
    :type blacklisted_names: typing.Iterable[str]
    :param blacklisted_exceptions: list of exception,
                                   which should be re-raised without
                                   producing log record.
    :type blacklisted_exceptions: typing.Iterable[BaseException]
    :param log_call_args: log call arguments before executing wrapped function.
    :type log_call_args: bool
    :param log_call_args_on_exc: log call arguments if exception raised.
    :type log_call_args_on_exc: bool
    :param log_result_obj: log result of function call.
    :type log_result_obj: bool

    .. note:: Attributes/properties names the same as argument names and changes
              the same fields.

    .. py:attribute:: log_level
    .. py:attribute:: exc_level
    .. py:attribute:: max_indent
    .. py:attribute:: blacklisted_names

        ``typing.List[str]``, modified via mutability
    .. py:attribute:: blacklisted_exceptions

        ``typing.List[Exception]``, modified via mutability
    .. py:attribute:: log_call_args
    .. py:attribute:: log_call_args_on_exc
    .. py:attribute:: log_result_obj

    .. py:method:: __call__(*args, **kwargs)

        :returns: Python 2.x: function

                  Python 3.4+: function or coroutine function (depends on decorated object)

        Decorator entry-point. Logic is stored separately and load depends on python version.


.. py:function:: logwrap(log=logging.getLogger('logwrap'), log_level=logging.DEBUG, exc_level=logging.ERROR, max_indent=20, spec=None, blacklisted_names=None, blacklisted_exceptions=None, log_call_args=True, log_call_args_on_exc=True, log_result_obj=True, )

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
    :type spec: callable
    :param blacklisted_names: Blacklisted argument names.
                              Arguments with this names will be skipped in log.

        .. versionadded:: 1.3.0
    :type blacklisted_names: typing.Iterable[str]
    :param blacklisted_exceptions: list of exception,
                                   which should be re-raised without
                                   producing log record.

        .. versionadded:: 2.2.0
    :type blacklisted_exceptions: typing.Iterable[BaseException]
    :param log_call_args: log call arguments before executing wrapped function.

        .. versionadded:: 2.2.0
    :type log_call_args: bool
    :param log_call_args_on_exc: log call arguments if exception raised.

        .. versionadded:: 2.2.0
    :type log_call_args_on_exc: bool

    :param log_result_obj: log result of function call.

        .. versionadded:: 2.2.0
    :type log_result_obj: bool

    :returns: LogWrap decorator instance
    :rtype: LogWrap

        .. versionchanged:: 2.2.0


.. py:class:: AsyncLogWrap

    .. versionadded:: 2.2.0

    .. deprecated:: 2.3.0

    .. attention:: Will be deleted on 2.4.0.


.. py:function:: async_logwrap

    .. versionadded:: 2.0.0

    .. deprecated:: 2.3.0

    .. attention:: Will be deleted on 2.4.0.
