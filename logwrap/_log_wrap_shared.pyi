import logging
import typing
from . import _class_decorator

logger: logging.Logger

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
