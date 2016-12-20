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

from __future__ import absolute_import
from __future__ import unicode_literals

import unittest

import logwrap
from logwrap import _repr_utils


class TestPrettyRepr(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(
            logwrap.pretty_repr(True), repr(True)
        )

    def test_text(self):
        self.assertEqual(
            logwrap.pretty_repr('Unicode text'), "u'''Unicode text'''"
        )
        self.assertEqual(
            logwrap.pretty_repr(b'bytes text\x01'), "b'''bytes text\x01'''"
        )

    def test_iterable(self):
        self.assertEqual(
            'list([{nl:<5}1,{nl:<5}2,{nl:<5}3,\n'
            '])'.format(nl='\n'),
            logwrap.pretty_repr([1, 2, 3]),
        )
        self.assertEqual(
            'tuple(({nl:<5}1,{nl:<5}2,{nl:<5}3,\n'
            '))'.format(nl='\n'),
            logwrap.pretty_repr((1, 2, 3)),
        )
        res = logwrap.pretty_repr({1, 2, 3})
        self.assertTrue(
            res.startswith('set({') and res.endswith('\n})')
        )

    def test_dict(self):
        self.assertEqual(
            'dict({\n'
            '    1 : 1,\n'
            '    2 : 2,\n'
            '    33: 33,\n'
            '})',
            logwrap.pretty_repr({1: 1, 2: 2, 33: 33}),
        )

    def test_nested_obj(self):
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
            'list([\n'
            '    dict({\n'
            '        1: 2,\n'
            '    }),\n'
            '    dict({\n'
            '        3: \n'
            '            set({\n'
            '                4,\n'
            '            }),\n'
            '    }),\n'
            '    list([\n'
            '        5,\n'
            '        6,\n'
            '        7,\n'
            '    ]),\n'
            '    tuple((\n'
            '        8,\n'
            '        9,\n'
            '        10,\n'
            '    )),\n'
            '    {},\n'
            '    [],\n'
            '    (),\n'
            '    set(),\n'
            '])'
        )
        self.assertEqual(exp_repr, logwrap.pretty_repr(test_obj))

    def test_prepare_repr(self):
        def empty_func():
            pass

        def full_func(arg, darg=1, *positional, **named):
            pass

        class TstClass(object):
            def tst_method(self, arg, darg=1, *positional, **named):
                pass

            @classmethod
            def tst_classmethod(cls, arg, darg=1, *positional, **named):
                pass

            @staticmethod
            def tst_staticmethod(arg, darg=1, *positional, **named):
                pass

        tst_instance = TstClass()

        self.assertEqual(
            list(_repr_utils._prepare_repr(empty_func)),
            []
        )

        self.assertEqual(
            list(_repr_utils._prepare_repr(full_func)),
            ['arg', ('darg', 1), '*positional', '**named']
        )

        self.assertEqual(
            list(_repr_utils._prepare_repr(TstClass.tst_method)),
            ['self', 'arg', ('darg', 1), '*positional', '**named']
        )

        self.assertEqual(
            list(_repr_utils._prepare_repr(TstClass.tst_classmethod)),
            [('cls', TstClass), 'arg', ('darg', 1), '*positional', '**named']
        )

        self.assertEqual(
            list(_repr_utils._prepare_repr(TstClass.tst_staticmethod)),
            ['arg', ('darg', 1), '*positional', '**named']
        )

        self.assertEqual(
            list(_repr_utils._prepare_repr(tst_instance.tst_method)),
            [
                ('self', tst_instance),
                'arg',
                ('darg', 1),
                '*positional',
                '**named',
            ]
        )

        self.assertEqual(
            list(_repr_utils._prepare_repr(tst_instance.tst_classmethod)),
            [('cls', TstClass), 'arg', ('darg', 1), '*positional', '**named']
        )

        self.assertEqual(
            list(_repr_utils._prepare_repr(tst_instance.tst_staticmethod)),
            ['arg', ('darg', 1), '*positional', '**named']
        )

    def test_callable(self):
        fmt = "\n{spc:<{indent}}<{obj!r} with interface ({args})>".format

        def empty_func():
            pass

        def full_func(arg, darg=1, *positional, **named):
            pass

        class TstClass(object):
            def tst_method(self, arg, darg=1, *positional, **named):
                pass

            @classmethod
            def tst_classmethod(cls, arg, darg=1, *positional, **named):
                pass

        tst_instance = TstClass()

        self.assertEqual(
            logwrap.pretty_repr(empty_func),
            fmt(spc='', indent=0, obj=empty_func, args='')
        )

        self.assertEqual(
            logwrap.pretty_repr(full_func),
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
            logwrap.pretty_repr(obj),
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
            logwrap.pretty_repr(obj),
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
            logwrap.pretty_repr(obj),
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
            logwrap.pretty_repr(obj),
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

    def test_indent(self):
        obj = [[[[[[[[[[123]]]]]]]]]]
        self.assertEqual(
            "list([\n"
            "    list([\n"
            "        list([\n"
            "            list([\n"
            "                list([\n"
            "                    list([\n"
            "                        list([\n"
            "                            list([\n"
            "                                list([\n"
            "                                    list([\n"
            "                                        123,\n"
            "                                    ]),\n"
            "                                ]),\n"
            "                            ]),\n"
            "                        ]),\n"
            "                    ]),\n"
            "                ]),\n"
            "            ]),\n"
            "        ]),\n"
            "    ]),\n"
            "])",
            logwrap.pretty_repr(obj, max_indent=40),
        )
        self.assertEqual(
            "list([\n"
            "    list([\n"
            "        list([\n"
            "            [[[[[[[123]]]]]]],\n"
            "        ]),\n"
            "    ]),\n"
            "])",
            logwrap.pretty_repr(obj, max_indent=10),
        )

    def test_magic_override(self):
        class Tst(object):
            def __repr__(self):
                return 'Test'

            def __pretty_repr__(
                self,
                parser,
                indent,
                no_indent_start
            ):
                return parser.process_element(
                    "<Test Class at 0x{:X}>".format(id(self.__class__)),
                    indent=indent,
                    no_indent_start=no_indent_start
                )

        result = logwrap.pretty_repr(Tst())
        self.assertNotEqual(
            result,
            'Test'
        )
        self.assertEqual(
            result,
            "u'''<Test Class at 0x{:X}>'''".format(id(Tst))
        )

    def test_py2_compatibility_flag(self):
        self.assertIsInstance(logwrap.pretty_repr(u'Text', py2_str=True), str)
