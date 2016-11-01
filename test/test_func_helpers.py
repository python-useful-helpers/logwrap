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

# pylint: disable=missing-docstring, unused-argument

from __future__ import absolute_import
from __future__ import unicode_literals

import unittest

import logwrap


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
