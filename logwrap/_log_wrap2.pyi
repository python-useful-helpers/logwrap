import logging
import typing
from . import _log_wrap_shared

class LogWrap(_log_wrap_shared.BaseLogWrap): ...

def logwrap(
    log: typing.Union[logging.Logger, typing.Callable]=...,
    log_level: int=...,
    exc_level: int=...,
    max_indent: int=...,
    spec: typing.Optional[typing.Callable]=...,
    blacklisted_names: typing.Optional[typing.List[str]]=...,
    blacklisted_exceptions: typing.Optional[typing.List[Exception]]=...,
    log_call_args: bool=...,
    log_call_args_on_exc: bool=...,
    log_result_obj: bool=...
) -> typing.Union[LogWrap, typing.Callable]: ...
