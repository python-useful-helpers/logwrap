import inspect
import logging
import typing

import six

from . import _class_decorator

logger: logging.Logger

def _check_type(expected: typing.Type) -> typing.Callable: ...

class BaseLogWrap(_class_decorator.BaseDecorator):
    def __init__(
        self,
        log: typing.Union[logging.Logger, typing.Callable]=...,
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

    def _get_func_args_repr(
        self,
        sig: inspect.Signature,
        args: typing.Tuple,
        kwargs: typing.Dict[str, typing.Any]
    ) -> six.text_type: ...

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
