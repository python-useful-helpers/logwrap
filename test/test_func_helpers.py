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

# pylint: disable=missing-docstring, unused-argument

from __future__ import absolute_import
from __future__ import unicode_literals

import unittest

import logwrap
# noinspection PyProtectedMember
from logwrap import _func_helpers


class TestFuncHelpers(unittest.TestCase):
    def test_get_arg_names(self):
        def func_no_args():
            pass

        def func_arg(single):
            pass

        def func_args(first, last):
            pass

        self.assertEqual(
            logwrap.get_arg_names(func_no_args),
            []
        )

        self.assertEqual(
            logwrap.get_arg_names(func_arg),
            ['single']
        )

        self.assertEqual(
            logwrap.get_arg_names(func_args),
            ['first', 'last']
        )

    def test_getcallargs(self):
        def func_no_def(arg1, arg2):
            pass

        def func_def(arg1, arg2='arg2'):
            pass

        self.assertEqual(
            dict(logwrap.get_call_args(func_no_def, *['arg1', 'arg2'], **{})),
            {'arg1': 'arg1', 'arg2': 'arg2'}
        )

        self.assertEqual(
            dict(
                logwrap.get_call_args(
                    func_no_def,
                    *['arg1'],
                    **{'arg2': 'arg2'}
                )),
            {'arg1': 'arg1', 'arg2': 'arg2'}
        )

        self.assertEqual(
            dict(logwrap.get_call_args(
                func_no_def, *[], **{'arg1': 'arg1', 'arg2': 'arg2'})),
            {'arg1': 'arg1', 'arg2': 'arg2'}
        )

        self.assertEqual(
            dict(logwrap.get_call_args(func_def, *['arg1'], **{})),
            {'arg1': 'arg1', 'arg2': 'arg2'}
        )

        self.assertEqual(
            dict(logwrap.get_call_args(func_def, *[], **{'arg1': 'arg1'})),
            {'arg1': 'arg1', 'arg2': 'arg2'}
        )

        self.assertEqual(
            dict(logwrap.get_call_args(
                func_def, *[], **{'arg1': 'arg1', 'arg2': 2})),
            {'arg1': 'arg1', 'arg2': 2}
        )

    def test_get_args_kwargs_names(self):
        def tst0():
            pass

        self.assertEqual(
            _func_helpers.get_args_kwargs_names(tst0),
            (None, None)
        )

        def tst1(a):
            pass

        self.assertEqual(
            _func_helpers.get_args_kwargs_names(tst1),
            (None, None)
        )

        def tst2(a, *positional):
            pass

        self.assertEqual(
            _func_helpers.get_args_kwargs_names(tst2),
            ('positional', None)
        )

        def tst3(a, **named):
            pass

        self.assertEqual(
            _func_helpers.get_args_kwargs_names(tst3),
            (None, 'named')
        )

        def tst4(a, *positional, **named):
            pass

        self.assertEqual(
            _func_helpers.get_args_kwargs_names(tst4),
            ('positional', 'named')
        )

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
            list(_func_helpers.prepare_repr(empty_func)),
            []
        )

        self.assertEqual(
            list(_func_helpers.prepare_repr(full_func)),
            ['arg', ('darg', 1), '*positional', '**named']
        )

        self.assertEqual(
            list(_func_helpers.prepare_repr(TstClass.tst_method)),
            ['self', 'arg', ('darg', 1), '*positional', '**named']
        )

        self.assertEqual(
            list(_func_helpers.prepare_repr(TstClass.tst_classmethod)),
            [('cls', TstClass), 'arg', ('darg', 1), '*positional', '**named']
        )

        self.assertEqual(
            list(_func_helpers.prepare_repr(TstClass.tst_staticmethod)),
            ['arg', ('darg', 1), '*positional', '**named']
        )

        self.assertEqual(
            list(_func_helpers.prepare_repr(tst_instance.tst_method)),
            [
                ('self', tst_instance),
                'arg',
                ('darg', 1),
                '*positional',
                '**named',
            ]
        )

        self.assertEqual(
            list(_func_helpers.prepare_repr(tst_instance.tst_classmethod)),
            [('cls', TstClass), 'arg', ('darg', 1), '*positional', '**named']
        )

        self.assertEqual(
            list(_func_helpers.prepare_repr(tst_instance.tst_staticmethod)),
            ['arg', ('darg', 1), '*positional', '**named']
        )
