import typing

import six

class PrettyFormat:
    def __init__(
        self,
        max_indent: int=...,
        indent_step: int=...,
        py2_str: bool=...
    ) -> None: ...

    @property
    def max_indent(self) -> int: ...

    @property
    def indent_step(self) -> int: ...

    def next_indent(self, indent: int, multiplier: int=...) -> int: ...

    def process_element(self, src: typing.Any, indent: int=..., no_indent_start: bool=...) -> six.text_type: ...

    def __call__(self, src: typing.Any, indent: int=..., no_indent_start: bool=...) -> typing.Union[six.text_type, str]: ...

class PrettyRepr(PrettyFormat): ...
class PrettyStr(PrettyFormat): ...

def pretty_repr(
    src: typing.Any,
    indent: int=...,
    no_indent_start: bool=...,
    max_indent: int=...,
    indent_step: int=...,
    py2_str: bool=...
) -> typing.Union[six.text_type, str]: ...

def pretty_str(
    src: typing.Any,
    indent: int=...,
    no_indent_start: bool=...,
    max_indent: int=...,
    indent_step: int=...,
    py2_str: bool=...
) -> typing.Union[six.text_type, str]: ...
