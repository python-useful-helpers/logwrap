.. LogOnAccess

API: LogOnAccess
========================

.. py:module:: logwrap
.. py:currentmodule:: logwrap


.. py:class:: LogOnAccess(property)

    Property with logging on successful get/set/delete or failure.

    .. versionadded:: 6.1.0

    .. py:method:: __init__(fget=None, fset=None, fdel=None, doc=None, *, logger=None, log_object_repr=True, log_level=logging.DEBUG, exc_level=logging.DEBUG, log_before=True, log_success=True, log_failure=True, log_traceback=True, override_name=None)

        :param fget: normal getter.
        :type fget: None | Callable[[typing.Any, ], typing.Any]
        :param fset: normal setter.
        :type fset: None | Callable[[typing.Any, typing.Any], None]
        :param fdel: normal deleter.
        :type fdel: None | Callable[[typing.Any, ], None]
        :param doc: docstring override
        :type doc: None | str
        :param logger: logger instance or name to use as override
        :type logger: None | logging.Logger | str
        :param log_object_repr: use `repr` over object to describe owner if True else owner class name and id
        :type log_object_repr: bool
        :param log_level: log level for successful operations
        :type log_level: int
        :param exc_level: log level for exceptions
        :type exc_level: int
        :param log_before: log before operation
        :type log_before: bool
        :param log_success: log successful operations
        :type log_success: bool
        :param log_failure: log exceptions
        :type log_failure: bool
        :param log_traceback: Log traceback on exceptions
        :type log_traceback: bool
        :param override_name: override property name if not None else use getter/setter/deleter name
        :type override_name: None | str

    .. py:method:: getter(fget)

        Descriptor to change the getter on a property.

        :param fget: new normal getter.
        :type fget: ``None | Callable[[typing.Any, ], typing.Any]``
        :rtype: ``AdvancedProperty``

    .. py:method:: setter(fset)

        Descriptor to change the setter on a property.

        :param fset: new setter.
        :type fset: ``None | Callable[[typing.Any, typing.Any], None]``
        :rtype: ``AdvancedProperty``

    .. py:method:: deleter(fdel)

        Descriptor to change the deleter on a property.

        :param fdel: New deleter.
        :type fdel: ``None | Callable[[typing.Any, ], None]``
        :rtype: ``AdvancedProperty``

    .. py:attribute:: fget

        ``None | Callable[[typing.Any, ], typing.Any]``
        Getter instance.

    .. py:attribute:: fset

        ``None | Callable[[typing.Any, typing.Any], None]``
        Setter instance.

    .. py:attribute:: fdel

        ``None | Callable[[typing.Any, ], None]``
        Deleter instance.

    .. py:attribute:: logger

        ``None | logging.Logger``
        Logger instance to use as override.

    .. py:attribute:: log_object_repr

        ``bool``
        Use `repr` over object to describe owner if True else owner class name and id.

    .. py:attribute:: log_level

        ``int``
        Log level for successful operations.

    .. py:attribute:: exc_level

        ``int``
        Log level for exceptions.

    .. py:attribute:: log_before

        ``bool``
        Log before operation

    .. py:attribute:: log_success

        ``bool``
        Log successful operations.

    .. py:attribute:: log_failure

        ``bool``
        Log exceptions.

    .. py:attribute:: log_traceback

        ``bool``
        Log traceback on exceptions.

    .. py:attribute:: override_name

        ``None | str``
        Override property name if not None else use getter/setter/deleter name.
