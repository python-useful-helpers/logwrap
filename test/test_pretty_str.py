#    Copyright 2016 Alexey Stepanov aka penguinolog

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

from __future__ import absolute_import
from __future__ import unicode_literals

import unittest

import logwrap


# noinspection PyUnusedLocal,PyMissingOrEmptyDocstring
class TestPrettyStr(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(
            logwrap.pretty_str(True), str(True)
        )

    def test_text(self):
        self.assertEqual(
            logwrap.pretty_str('Unicode text'), "Unicode text"
        )
        self.assertEqual(
            logwrap.pretty_str(b'bytes text\x01'), "bytes text\x01"
        )

    def test_iterable(self):
        self.assertEqual(
            '[{nl:<5}1,{nl:<5}2,{nl:<5}3,\n'
            ']'.format(nl='\n'),
            logwrap.pretty_str([1, 2, 3]),
        )
        self.assertEqual(
            '({nl:<5}1,{nl:<5}2,{nl:<5}3,\n'
            ')'.format(nl='\n'),
            logwrap.pretty_str((1, 2, 3)),
        )
        res = logwrap.pretty_str({1, 2, 3})
        self.assertTrue(
            res.startswith('{') and res.endswith('\n}')
        )
        res = logwrap.pretty_str(frozenset({1, 2, 3}))
        self.assertTrue(
            res.startswith('{') and res.endswith('\n}')
        )

    def test_simple_set(self):
        self.assertEqual(
            logwrap.pretty_str(set()),
            'set()'
        )

    def test_dict(self):
        self.assertEqual(
            '{\n'
            '    1 : 1,\n'
            '    2 : 2,\n'
            '    33: 33,\n'
            '}',
            logwrap.pretty_str({1: 1, 2: 2, 33: 33}),
        )

    def test_callable(self):
        fmt = "\n{spc:<{indent}}<{obj!s} with interface ({args})>".format

        def empty_func():
            pass

        def full_func(arg, darg=1, *positional, **named):
            pass

        # noinspection PyMissingOrEmptyDocstring
        class TstClass(object):
            def tst_method(self, arg, darg=1, *positional, **named):
                pass

            @classmethod
            def tst_classmethod(cls, arg, darg=1, *positional, **named):
                pass

        tst_instance = TstClass()

        self.assertEqual(
            logwrap.pretty_str(empty_func),
            fmt(spc='', indent=0, obj=empty_func, args='')
        )

        self.assertEqual(
            logwrap.pretty_str(full_func),
            fmt(
                spc='',
                indent=0,
                obj=full_func,
                args='\n'
                '    arg,\n'
                '    darg=1,\n'
                '    *positional,\n'
                '    **named,\n'
            )
        )

        obj = TstClass.tst_method

        self.assertEqual(
            logwrap.pretty_str(obj),
            fmt(
                spc='',
                indent=0,
                obj=obj,
                args='\n'
                     '    self,\n'
                     '    arg,\n'
                     '    darg=1,\n'
                     '    *positional,\n'
                     '    **named,\n'
            )
        )

        obj = TstClass.tst_classmethod

        self.assertEqual(
            logwrap.pretty_str(obj),
            fmt(
                spc='',
                indent=0,
                obj=obj,
                args='\n'
                     '    cls={cls!r},\n'
                     '    arg,\n'
                     '    darg=1,\n'
                     '    *positional,\n'
                     '    **named,\n'.format(cls=TstClass)
            )
        )

        obj = tst_instance.tst_method

        self.assertEqual(
            logwrap.pretty_str(obj),
            fmt(
                spc='',
                indent=0,
                obj=obj,
                args='\n'
                     '    self={self!r},\n'
                     '    arg,\n'
                     '    darg=1,\n'
                     '    *positional,\n'
                     '    **named,\n'.format(self=tst_instance)
            )
        )

        obj = tst_instance.tst_classmethod

        self.assertEqual(
            logwrap.pretty_str(obj),
            fmt(
                spc='',
                indent=0,
                obj=obj,
                args='\n'
                     '    cls={cls!r},\n'
                     '    arg,\n'
                     '    darg=1,\n'
                     '    *positional,\n'
                     '    **named,\n'.format(cls=TstClass)
            )
        )

    def test_magic_override(self):
        # noinspection PyMissingOrEmptyDocstring
        class Tst(object):
            def __str__(self):
                return 'Test'

            # noinspection PyMethodMayBeStatic
            def __pretty_str__(
                self,
                parser,
                indent,
                no_indent_start
            ):
                return parser.process_element(
                    "Test Class",
                    indent=indent,
                    no_indent_start=no_indent_start
                )

        result = logwrap.pretty_str(Tst())
        self.assertNotEqual(
            result,
            'Test'
        )
        self.assertEqual(
            result,
            "Test Class".format(id(Tst))
        )

    def test_py2_compatibility_flag(self):
        self.assertIsInstance(logwrap.pretty_str(u'Text', py2_str=True), str)
