#    Copyright 2016 Mirantis, Inc.
#    Copyright 2016 Alexey Stepanov aka penguinolog
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

    def test_nested_dict(self):
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
            '   }),\n'
            '    dict({\n'
            '        3: \n'
            '            set({\n'
            '                4,\n'
            '           }),\n'
            '   }),\n'
            '    list([\n'
            '        5,\n'
            '        6,\n'
            '        7,\n'
            '   ]),\n'
            '    tuple((\n'
            '        8,\n'
            '        9,\n'
            '        10,\n'
            '   )),\n'
            '    {},\n'
            '    [],\n'
            '    (),\n'
            '    %s,\n'
            '])' % repr(set())
        )
        self.assertEqual(logwrap.pretty_repr(test_obj), exp_repr)
