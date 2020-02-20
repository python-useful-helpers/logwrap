#    Copyright 2018 - 2020 Alexey Stepanov aka penguinolog
#
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

"""Base class for decorators."""

import functools
import typing

ReturnType = typing.TypeVar("ReturnType")


cdef class BaseDecorator:
    """Base class for decorators.

    Implements wrapping and __call__, wrapper getter is abstract.

    .. note:: wrapper getter is called only on function call, if decorator used without braces.

    Usage example:

    >>> class TestDecorator(BaseDecorator):
    ...     def _get_function_wrapper(self, func):
    ...         print('Wrapping: {}'.format(func.__name__))
    ...         @functools.wraps(func)
    ...         def wrapper(*args, **kwargs):
    ...             print('call_function: {}'.format(func.__name__))
    ...             return func(*args, **kwargs)
    ...         return wrapper

    >>> @TestDecorator
    ... def func_no_init():
    ...     pass
    >>> func_no_init()
    Wrapping: func_no_init
    call_function: func_no_init
    >>> isinstance(func_no_init, TestDecorator)
    True
    >>> func_no_init._func is func_no_init.__wrapped__
    True

    >>> @TestDecorator()
    ... def func_init():
    ...     pass
    Wrapping: func_init
    >>> func_init()
    call_function: func_init
    >>> isinstance(func_init, TestDecorator)
    False
    """

    def __init__(self, func: typing.Optional[typing.Callable[..., ReturnType]] = None) -> None:
        """Decorator.

        :param func: function to wrap
        :type func: typing.Optional[typing.Callable]
        """
        super().__init__()
        self._func = func
        if self._func is not None:
            functools.update_wrapper(self, self._func)

    def _get_function_wrapper(self, func: typing.Callable[..., ReturnType]) -> typing.Callable[..., ReturnType]:
        """Here should be constructed and returned real decorator.

        :param func: Wrapped function
        :type func: typing.Callable
        :return: function wrapper
        :rtype: typing.Callable
        """
        raise NotImplementedError()

    def __call__(self, *args: typing.Union[typing.Callable[..., ReturnType], typing.Any], **kwargs: typing.Any) -> typing.Union[typing.Callable[..., ReturnType], ReturnType]:
        """Main decorator getter.

        :return: decorated function if it provided via arguments else function result
        :rtype: typing.Union[typing.Callable[..., ReturnType], ReturnType]
        """
        cdef list l_args = list(args)

        if self._func:
            wrapped = self._func
        else:
            wrapped = l_args.pop(0)

        wrapper = self._get_function_wrapper(wrapped)
        if self._func:
            return wrapper(*l_args, **kwargs)
        return wrapper

    def __repr__(self) -> str:
        """For debug purposes.

        :return: representation for logging/debug purposes
        :rtype: str
        """
        return f"<{self.__class__.__name__}({self._func!r}) at 0x{id(self):X}>"
