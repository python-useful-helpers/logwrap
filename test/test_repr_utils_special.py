#    Copyright 2016-2021 Alexey Stepanov aka penguinolog

#    Copyright 2016 Mirantis, Inc.

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

# pylint: disable=missing-docstring

"""_repr_utils (internal helpers) specific tests."""

import typing
import unittest

import logwrap


# noinspection PyUnusedLocal
class TestPrettyRepr(unittest.TestCase):
    def test_001_dict_subclass(self):
        class MyDict(dict):
            """Dict subclass."""

        val = MyDict(key="value")
        self.assertEqual("MyDict({\n    'key': 'value',\n})", logwrap.pretty_repr(val))

        self.assertEqual("{\n    key: value,\n}", logwrap.pretty_str(val))

    def test_002_typing_specific_dict(self):
        class MyDict(typing.Dict[str, str]):
            """Dict subclass."""

        val = MyDict(key="value")
        self.assertEqual("MyDict({\n    'key': 'value',\n})", logwrap.pretty_repr(val))

        self.assertEqual("{\n    key: value,\n}", logwrap.pretty_str(val))

    def test_003_typing_specific_dict_repr_override(self):
        class MyDict(typing.Dict[str, str]):
            """Dict subclass."""

            def __repr__(self) -> str:
                return f"{self.__class__.__name__}({tuple(zip(self.items()))})"

            def __str__(self) -> str:
                return str(dict(self))

        val = MyDict(key="value")
        self.assertEqual("MyDict(((('key', 'value'),),))", logwrap.pretty_repr(val))

        self.assertEqual("{'key': 'value'}", logwrap.pretty_str(val))

    def test_004_typed_dict(self):
        # noinspection PyMissingOrEmptyDocstring
        class MyDict(typing.TypedDict):
            key: str

        val = MyDict(key="value")
        self.assertEqual("{\n    'key': 'value',\n}", logwrap.pretty_repr(val))

        self.assertEqual("{\n    key: value,\n}", logwrap.pretty_str(val))
