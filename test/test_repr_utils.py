#    Copyright 2016 - 2021 Alexey Stepanov aka penguinolog

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

from __future__ import annotations

# Standard Library
import typing
import unittest

# Package Implementation
import logwrap


# noinspection PyUnusedLocal,PyMissingOrEmptyDocstring
class TestPrettyRepr(unittest.TestCase):
    def test_001_simple(self):
        self.assertEqual(logwrap.pretty_repr(True), repr(True))

    def test_002_text(self):
        txt = "Unicode text"
        b_txt = b"bytes text\x01"
        self.assertEqual(repr(txt), logwrap.pretty_repr(txt))
        self.assertEqual(repr(b_txt), logwrap.pretty_repr(b_txt))

    def test_003_iterable(self):
        self.assertEqual(
            "[{nl:<5}1,{nl:<5}2,{nl:<5}3,\n]".format(nl="\n"),
            logwrap.pretty_repr([1, 2, 3]),
        )
        self.assertEqual(
            "({nl:<5}1,{nl:<5}2,{nl:<5}3,\n)".format(nl="\n"),
            logwrap.pretty_repr((1, 2, 3)),
        )
        res = logwrap.pretty_repr({1, 2, 3})
        self.assertTrue(res.startswith("{") and res.endswith("\n}"))
        res = logwrap.pretty_repr(frozenset({1, 2, 3}))
        self.assertTrue(res.startswith("frozenset({") and res.endswith("\n})"))

    def test_004_dict(self):
        self.assertEqual(
            "{\n" "    1 : 1,\n" "    2 : 2,\n" "    33: 33,\n" "}",
            logwrap.pretty_repr({1: 1, 2: 2, 33: 33}),
        )

    def test_005_nested_obj(self):
        test_obj = [
            {1: 2},
            {3: {4}},
            [5, 6, 7],
            (8, 9, 10),
            {},
            [],
            (),
            set(),
        ]
        exp_repr = (
            "[\n"
            "    {\n"
            "        1: 2,\n"
            "    },\n"
            "    {\n"
            "        3: {\n"
            "            4,\n"
            "        },\n"
            "    },\n"
            "    [\n"
            "        5,\n"
            "        6,\n"
            "        7,\n"
            "    ],\n"
            "    (\n"
            "        8,\n"
            "        9,\n"
            "        10,\n"
            "    ),\n"
            "    {},\n"
            "    [],\n"
            "    (),\n"
            "    set(),\n"
            "]"
        )
        self.assertEqual(exp_repr, logwrap.pretty_repr(test_obj))

    def test_006_callable_simple(self):
        def empty_func():
            pass

        self.assertEqual(
            f"{'':<{0}}"
            f"<{empty_func.__class__.__name__} {empty_func.__module__}.{empty_func.__name__} with interface ({''})>",
            logwrap.pretty_repr(empty_func),
        )

    def test_007_callable_with_args(self):
        def full_func(arg, darg=1, *positional, **named):
            pass

        args = "\n" "    arg,\n" "    darg=1,\n" "    *positional,\n" "    **named,\n"

        self.assertEqual(
            f"{'':<{0}}"
            f"<{full_func.__class__.__name__} {full_func.__module__}.{full_func.__name__} with interface ({args})>",
            logwrap.pretty_repr(full_func),
        )

    def test_008_callable_class_elements(self):
        # noinspection PyMissingOrEmptyDocstring
        class TstClass(object):
            def tst_method(self, arg, darg=1, *positional, **named):
                pass

            @classmethod
            def tst_classmethod(cls, arg, darg=1, *positional, **named):
                pass

        tst_instance = TstClass()

        c_m_args = "\n" "    self,\n" "    arg,\n" "    darg=1,\n" "    *positional,\n" "    **named,\n"

        cm_args = (
            "\n"
            "    cls={cls!r},\n"
            "    arg,\n"
            "    darg=1,\n"
            "    *positional,\n"
            "    **named,\n".format(cls=TstClass)
        )

        i_m_args = (
            f"\n" f"    self={tst_instance!r},\n" f"    arg,\n" f"    darg=1,\n" f"    *positional,\n" f"    **named,\n"
        )

        for callable_obj, args in (
            (TstClass.tst_method, c_m_args),
            (TstClass.tst_classmethod, cm_args),
            (tst_instance.tst_method, i_m_args),
            (tst_instance.tst_classmethod, cm_args),
        ):

            self.assertEqual(
                f"{'':<{0}}"
                f"<{callable_obj.__class__.__name__} {callable_obj.__module__}.{callable_obj.__name__} "
                f"with interface ({args})>",
                logwrap.pretty_repr(callable_obj),
            )

    def test_009_indent(self):
        obj = [[[[[[[[[[123]]]]]]]]]]
        self.assertEqual(
            "[\n"
            "    [\n"
            "        [\n"
            "            [\n"
            "                [\n"
            "                    [\n"
            "                        [\n"
            "                            [\n"
            "                                [\n"
            "                                    [\n"
            "                                        123,\n"
            "                                    ],\n"
            "                                ],\n"
            "                            ],\n"
            "                        ],\n"
            "                    ],\n"
            "                ],\n"
            "            ],\n"
            "        ],\n"
            "    ],\n"
            "]",
            logwrap.pretty_repr(obj, max_indent=40),
        )
        self.assertEqual(
            "[\n" "    [\n" "        [\n" "            [[[[[[[123]]]]]]],\n" "        ],\n" "    ],\n" "]",
            logwrap.pretty_repr(obj, max_indent=10),
        )

    def test_010_magic_override(self):
        # noinspection PyMissingOrEmptyDocstring
        class Tst(object):
            def __repr__(self):
                return "Test"

            def __pretty_repr__(self, parser, indent, no_indent_start):
                return parser.process_element(
                    f"<Test Class at 0x{id(self.__class__):X}>", indent=indent, no_indent_start=no_indent_start
                )

        result = logwrap.pretty_repr(Tst())
        self.assertNotEqual(result, "Test")
        self.assertEqual(result, f"'<Test Class at 0x{id(Tst):X}>'")


# noinspection PyUnusedLocal,PyMissingOrEmptyDocstring
class TestAnnotated(unittest.TestCase):
    def test_001_annotation_args(self):
        def func(a: typing.Optional[int] = None):
            pass

        args = "\n    a: typing.Optional[int]=None,\n"

        self.assertEqual(
            f"{'':<{0}}<{func.__class__.__name__} {func.__module__}.{func.__name__} with interface ({args}){''}>",
            logwrap.pretty_repr(func),
        )

    def test_002_annotation_return(self):
        def func() -> None:
            pass

        self.assertEqual(
            f"{'':<{0}}<{func.__class__.__name__} {func.__module__}.{func.__name__} with interface ({''}){' -> None'}>",
            logwrap.pretty_repr(func),
        )

    def test_003_complex(self):
        def func(a: typing.Optional[int] = None) -> None:
            pass

        args = "\n    a: typing.Optional[int]=None,\n"

        self.assertEqual(
            f"{'':<{0}}"
            f"<{func.__class__.__name__} {func.__module__}.{func.__name__} with interface ({args}){' -> None'}>",
            logwrap.pretty_repr(func),
        )
