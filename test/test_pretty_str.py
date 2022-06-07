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

"""pretty_str specific tests"""

# Standard Library
import unittest

# Package Implementation
import logwrap


# noinspection PyUnusedLocal
class TestPrettyStr(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(logwrap.pretty_str(True), str(True))

    def test_text(self):
        self.assertEqual(logwrap.pretty_str("Unicode text"), "Unicode text")
        self.assertEqual(logwrap.pretty_str(b"bytes text\x01"), "bytes text\x01")

    def test_iterable(self):
        self.assertEqual(
            "[{nl:<5}1,{nl:<5}2,{nl:<5}3,\n" "]".format(nl="\n"),
            logwrap.pretty_str([1, 2, 3]),
        )
        self.assertEqual(
            "({nl:<5}1,{nl:<5}2,{nl:<5}3,\n" ")".format(nl="\n"),
            logwrap.pretty_str((1, 2, 3)),
        )
        res = logwrap.pretty_str({1, 2, 3})
        self.assertTrue(res.startswith("{") and res.endswith("\n}"))
        res = logwrap.pretty_str(frozenset({1, 2, 3}))
        self.assertTrue(res.startswith("{") and res.endswith("\n}"))

    def test_simple_set(self):
        self.assertEqual(logwrap.pretty_str(set()), "set()")

    def test_dict(self):
        self.assertEqual(
            "{\n" "    1 : 1,\n" "    2 : 2,\n" "    33: 33,\n" "}",
            logwrap.pretty_str({1: 1, 2: 2, 33: 33}),
        )

    def test_magic_override(self):
        # noinspection PyMissingOrEmptyDocstring
        class Tst:
            def __str__(self):
                return "Test"

            # noinspection PyMethodMayBeStatic
            def __pretty_str__(self, parser, indent, no_indent_start):
                return parser.process_element("Test Class", indent=indent, no_indent_start=no_indent_start)

        result = logwrap.pretty_str(Tst())
        self.assertNotEqual(result, "Test")
        self.assertEqual(result, "Test Class")  # .format(id(Tst))
