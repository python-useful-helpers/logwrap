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
            logwrap.pretty_repr([1, 2, 3]),
            '\n'
            'list([{nl:<5}1,{nl:<5}2,{nl:<5}3,\n'
            '])'.format(nl='\n')
        )
        self.assertEqual(
            logwrap.pretty_repr((1, 2, 3)),
            '\n'
            'tuple(({nl:<5}1,{nl:<5}2,{nl:<5}3,\n'
            '))'.format(nl='\n')
        )
        res = logwrap.pretty_repr({1, 2, 3})
        self.assertTrue(
            res.startswith('\nset({') and res.endswith('\n})')
        )

    def test_dict(self):
        self.assertEqual(
            logwrap.pretty_repr({1: 1, 2: 2, 33: 33}),
            '\n'
            'dict({\n'
            '    1 : 1,\n'
            '    2 : 2,\n'
            '    33: 33,\n'
            '})'
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
            '\n'
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
        self.assertEqual(logwrap.pretty_repr(test_obj), exp_repr)

    def test_callable(self):
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
            '\n<{}() at 0x{:X}>'.format(empty_func.__name__, id(empty_func))
        )

        self.assertEqual(
            logwrap.pretty_repr(full_func),
            '\n<{}(\n'
            '    arg,\n'
            '    darg=1,\n'
            '    *positional,\n'
            '    **named,\n'
            ') at 0x{:X}>'.format(full_func.__name__, id(full_func))
        )

        obj = TstClass.tst_method

        self.assertEqual(
            logwrap.pretty_repr(obj),
            '\n<{}(\n'
            '    self,\n'
            '    arg,\n'
            '    darg=1,\n'
            '    *positional,\n'
            '    **named,\n'
            ') at 0x{:X}>'.format(
                obj.__name__,
                id(obj)
            )
        )

        obj = TstClass.tst_classmethod

        self.assertEqual(
            logwrap.pretty_repr(obj),
            '\n<{cls_name}.{obj}(\n'
            '    cls={cls!r},\n'
            '    arg,\n'
            '    darg=1,\n'
            '    *positional,\n'
            '    **named,\n'
            ') at 0x{id:X}>'.format(
                cls_name=TstClass.__name__,
                obj=obj.__name__,
                cls=TstClass,
                id=id(obj)
            )
        )

        obj = tst_instance.tst_method

        self.assertEqual(
            logwrap.pretty_repr(obj),
            '\n<{cls_name}.{obj}(\n'
            '    self={cls!r},\n'
            '    arg,\n'
            '    darg=1,\n'
            '    *positional,\n'
            '    **named,\n'
            ') at 0x{id:X}>'.format(
                cls_name=tst_instance.__class__.__name__,
                obj=obj.__name__,
                cls=tst_instance,
                id=id(obj)
            )
        )

        obj = tst_instance.tst_classmethod

        self.assertEqual(
            logwrap.pretty_repr(obj),
            '\n<{cls_name}.{obj}(\n'
            '    cls={cls!r},\n'
            '    arg,\n'
            '    darg=1,\n'
            '    *positional,\n'
            '    **named,\n'
            ') at 0x{id:X}>'.format(
                cls_name=tst_instance.__class__.__name__,
                obj=obj.__name__,
                cls=tst_instance.__class__,
                id=id(obj)
            )
        )
