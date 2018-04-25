import abc
import types
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

    @abc.abstractmethod
    def _repr_callable(
        self,
        src: typing.Union[types.FunctionType, types.MethodType],
        indent: int=0
    ) -> six.text_type: ...

    @abc.abstractmethod
    def _repr_simple(
        self,
        src: typing.Any,
        indent: int=0,
        no_indent_start: bool=False
    ) -> six.text_type: ...

    @abc.abstractmethod
    def _repr_dict_items(
        self,
        src: typing.Dict,
        indent: int=0
    ) -> typing.Iterator[str]: ...

    @staticmethod
    def _repr_iterable_item(
        nl: bool,
        obj_type: str,
        prefix: str,
        indent: int,
        result: str,
        suffix: str,
    ) -> six.text_type: ...

    def _repr_iterable_items(
        self,
        src: typing.Iterable,
        indent: int=0
    ) -> typing.Iterator[str]: ...

    @property
    @abc.abstractmethod
    def _magic_method_name(self) -> six.text_type: ...

    def process_element(self, src: typing.Any, indent: int=..., no_indent_start: bool=...) -> six.text_type: ...

    def __call__(self, src: typing.Any, indent: int=..., no_indent_start: bool=...) -> typing.Union[six.text_type, str]: ...

class PrettyRepr(PrettyFormat):
    @property
    def _magic_method_name(self) -> six.text_type: ...

    @staticmethod
    def _strings_repr(
        indent: int,
        val: typing.Union[six.binary_type, six.text_type]
    ) -> six.text_type: ...

    def _repr_simple(
        self,
        src: typing.Any,
        indent: int=0,
        no_indent_start: bool=False
    ) -> six.text_type: ...

    def _repr_dict_items(
        self,
        src: typing.Dict,
        indent: int=0
    ) -> typing.Iterator[str]: ...

    def _repr_callable(
        self,
        src: typing.Union[types.FunctionType, types.MethodType],
        indent: int=0
    ) -> six.text_type: ...

    @staticmethod
    def _repr_iterable_item(
        nl: bool,
        obj_type: str,
        prefix: str,
        indent: int,
        result: str,
        suffix: str,
    ) -> six.text_type: ...

class PrettyStr(PrettyFormat):
    @property
    def _magic_method_name(self) -> six.text_type: ...

    @staticmethod
    def _strings_str(
        indent: int,
        val: typing.Union[six.binary_type, six.text_type]
    ) -> six.text_type: ...

    def _repr_simple(
        self,
        src: typing.Any,
        indent: int=0,
        no_indent_start: bool=False
    ) -> six.text_type: ...

    def _repr_dict_items(
        self,
        src: typing.Dict,
        indent: int=0
    ) -> typing.Iterator[str]: ...

    def _repr_callable(
        self,
        src: typing.Union[types.FunctionType, types.MethodType],
        indent: int=0
    ) -> six.text_type: ...

    @staticmethod
    def _repr_iterable_item(
        nl: bool,
        obj_type: str,
        prefix: str,
        indent: int,
        result: str,
        suffix: str,
    ) -> six.text_type: ...

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
