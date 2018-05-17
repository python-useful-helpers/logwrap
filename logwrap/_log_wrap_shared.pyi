import enum
import inspect
import logging
import typing

import six

from . import _class_decorator

if six.PY3:
    from inspect import Parameter
    from inspect import Signature
else:
    from funcsigs import Parameter
    from funcsigs import Signature


logger: logging.Logger

def _check_type(expected: typing.Type) -> typing.Callable: ...


class BoundParameter(object):

    __slots__ = (
        '_parameter',
        '_value'
    )

    POSITIONAL_ONLY = Parameter.POSITIONAL_ONLY
    POSITIONAL_OR_KEYWORD = Parameter.POSITIONAL_OR_KEYWORD
    VAR_POSITIONAL = Parameter.VAR_POSITIONAL
    KEYWORD_ONLY = Parameter.KEYWORD_ONLY
    VAR_KEYWORD = Parameter.VAR_KEYWORD

    empty = Parameter.empty  # type: typing.Type

    def __init__(
        self,
        parameter: Parameter,
        value: typing.Any=...
    ) -> None: ...

    @property
    def parameter(self) -> Parameter: ...

    @property
    def name(self) -> typing.Union[None, str]: ...

    @property
    def default(self) -> typing.Any: ...

    @property
    def annotation(self) -> typing.Union[Parameter.empty, str]: ...

    @property
    def kind(self) -> enum.IntEnum: ...

    @property
    def value(self) -> typing.Any: ...


def bind_args_kwargs(
        sig: Signature,
        *args,
        **kwargs
    ) -> typing.Iterator[BoundParameter]: ...


class BaseLogWrap(_class_decorator.BaseDecorator):
    def __init__(
        self,
        func: typing.Optional[typing.Callable]=None,
        log: logging.Logger=...,
        log_level: int=...,
        exc_level: int=...,
        max_indent: int=...,
        spec: typing.Optional[typing.Callable]=...,
        blacklisted_names: typing.Optional[typing.Iterable[str]]=...,
        blacklisted_exceptions: typing.Optional[typing.Iterable[Exception]]=...,
        log_call_args: bool=...,
        log_call_args_on_exc: bool=...,
        log_result_obj: bool=...
    ) -> None: ...

    @property
    def log_level(self) -> int: ...

    @log_level.setter
    def log_level(self, val: int) -> None: ...

    @property
    def exc_level(self) -> int: ...

    @exc_level.setter
    def exc_level(self, val: int) -> None: ...

    @property
    def max_indent(self) -> int: ...

    @max_indent.setter
    def max_indent(self, val: int) -> None: ...

    @property
    def blacklisted_names(self) -> typing.List[str]: ...

    @property
    def blacklisted_exceptions(self) -> typing.List[Exception]: ...

    @property
    def log_call_args(self) -> bool: ...

    @log_call_args.setter
    def log_call_args(self, val: bool) -> None: ...

    @property
    def log_call_args_on_exc(self) -> bool: ...

    @log_call_args_on_exc.setter
    def log_call_args_on_exc(self, val: bool) -> None: ...

    @property
    def log_result_obj(self) -> bool: ...

    @log_result_obj.setter
    def log_result_obj(self, val: bool) -> None: ...

    @property
    def _logger(self) -> logging.Logger: ...

    @property
    def _spec(self) -> typing.Callable: ...

    @staticmethod
    def _bind_args_kwargs(
        sig: Signature,
        *args,
        **kwargs
    ) -> typing.Iterator[BoundParameter]: ...

    def pre_process_param(
        self,
        arg: BoundParameter,
    ) -> typing.Union[BoundParameter, typing.Tuple[BoundParameter, typing.Any], None]: ...

    def post_process_param(
        self,
        arg: BoundParameter,
        arg_repr: typing.Text
    ) -> typing.Text: ...

    def _get_func_args_repr(
        self,
        sig: inspect.Signature,
        args: typing.Tuple,
        kwargs: typing.Dict[str, typing.Any]
    ) -> typing.Text: ...

    def _make_done_record(
        self,
        func_name: str,
        result: typing.Any
    ) -> None: ...

    def _make_calling_record(
        self,
        name: str,
        arguments: str,
        method: str='Calling',
    ) -> None: ...

    def _make_exc_record(
        self,
        name: str,
        arguments: str
    ) -> None: ...
