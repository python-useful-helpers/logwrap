#    Copyright 2016-2019 Alexey Stepanov aka penguinolog
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


cdef class BaseDecorator:
    """Base class for decorators.

    Implements wrapping and __call__, wrapper getter is abstract.

    .. note:: wrapper getter is called only on function call, if decorator used without braces.
    """

    def __init__(self, func: typing.Optional[typing.Callable[..., typing.Any]] = None) -> None:
        """Decorator.

        :param func: function to wrap
        :type func: typing.Optional[typing.Callable]
        """
        # noinspection PyArgumentList
        super(BaseDecorator, self).__init__()
        self._func = func
        if self._func is not None:
            functools.update_wrapper(self, self._func)

    def _get_function_wrapper(self, func: typing.Callable[..., typing.Any]) -> typing.Callable[..., typing.Any]:
        """Here should be constructed and returned real decorator.

        :param func: Wrapped function
        :type func: typing.Callable
        :rtype: typing.Callable
        """
        raise NotImplementedError()

    def __call__(self, *args: typing.Union[typing.Callable[..., typing.Any], typing.Any], **kwargs: typing.Any) -> typing.Any:
        """Main decorator getter."""
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
        """For debug purposes."""
        return "<{cls}({func!r}) at 0x{id:X}>".format(
            cls=self.__class__.__name__, func=self._func, id=id(self)
        )  # pragma: no cover
