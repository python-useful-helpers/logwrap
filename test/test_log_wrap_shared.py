#    Copyright 2018 Alexey Stepanov aka penguinolog

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

from __future__ import absolute_import
from __future__ import unicode_literals

import sys
import unittest

import six

# noinspection PyProtectedMember
from logwrap import _log_wrap_shared

# pylint: disable=ungrouped-imports, no-name-in-module
if six.PY3:  # pragma: no cover
    from inspect import signature
else:  # pragma: no cover
    # noinspection PyUnresolvedReferences
    from funcsigs import signature
# pylint: enable=ungrouped-imports, no-name-in-module


def example_function(
    arg1, arg2=2, arg3=3, *args, **kwargs
):
    pass


sig = signature(example_function)


# noinspection PyUnusedLocal,PyMissingOrEmptyDocstring
class TestBind(unittest.TestCase):
    def test_001_positive(self):
        params = list(_log_wrap_shared.bind_args_kwargs(sig, 1, arg3=33))
        arg_1_bound = params[0]
        self.assertEqual(arg_1_bound.name, 'arg1')
        self.assertEqual(arg_1_bound.value, 1)
        self.assertEqual(arg_1_bound.default, arg_1_bound.empty)
        self.assertEqual(arg_1_bound.annotation, arg_1_bound.empty)
        self.assertEqual(arg_1_bound.kind, arg_1_bound.POSITIONAL_OR_KEYWORD)
        self.assertEqual(str(arg_1_bound), "arg1=1")

        arg_2_bound = params[1]
        self.assertEqual(arg_2_bound.name, 'arg2')
        self.assertEqual(arg_2_bound.value, 2)
        self.assertEqual(arg_2_bound.default, 2)
        self.assertEqual(arg_2_bound.annotation, arg_2_bound.empty)
        self.assertEqual(arg_2_bound.kind, arg_2_bound.POSITIONAL_OR_KEYWORD)
        self.assertEqual(str(arg_2_bound), "arg2=2  # 2")

        arg_3_bound = params[2]
        self.assertEqual(arg_3_bound.name, 'arg3')
        self.assertEqual(arg_3_bound.value, 33)
        self.assertEqual(arg_3_bound.default, 3)
        self.assertEqual(arg_3_bound.annotation, arg_3_bound.empty)
        self.assertEqual(arg_3_bound.kind, arg_3_bound.POSITIONAL_OR_KEYWORD)
        self.assertEqual(str(arg_3_bound), "arg3=33  # 3")

        args_bound = params[3]
        self.assertEqual(args_bound.name, 'args')
        self.assertEqual(args_bound.value, args_bound.empty)
        self.assertEqual(args_bound.default, args_bound.empty)
        self.assertEqual(args_bound.annotation, args_bound.empty)
        self.assertEqual(args_bound.kind, args_bound.VAR_POSITIONAL)
        self.assertEqual(str(args_bound), "*args=()")

        kwargs_bound = params[4]
        self.assertEqual(kwargs_bound.name, 'kwargs')
        self.assertEqual(kwargs_bound.value, kwargs_bound.empty)
        self.assertEqual(kwargs_bound.default, kwargs_bound.empty)
        self.assertEqual(kwargs_bound.annotation, kwargs_bound.empty)
        self.assertEqual(kwargs_bound.kind, kwargs_bound.VAR_KEYWORD)
        self.assertEqual(str(kwargs_bound), "**kwargs={}")

    def test_002_args_kwargs(self):
        params = list(_log_wrap_shared.bind_args_kwargs(sig, 1, 2, 3, 4, arg5=5))

        args_bound = params[3]
        self.assertEqual(args_bound.name, 'args')
        self.assertEqual(args_bound.value, (4,))
        self.assertEqual(args_bound.default, args_bound.empty)
        self.assertEqual(args_bound.annotation, args_bound.empty)
        self.assertEqual(args_bound.kind, args_bound.VAR_POSITIONAL)
        self.assertEqual(str(args_bound), "*args=(4,)")

        kwargs_bound = params[4]
        self.assertEqual(kwargs_bound.name, 'kwargs')
        self.assertEqual(kwargs_bound.value, {'arg5': 5})
        self.assertEqual(kwargs_bound.default, kwargs_bound.empty)
        self.assertEqual(kwargs_bound.annotation, kwargs_bound.empty)
        self.assertEqual(kwargs_bound.kind, kwargs_bound.VAR_KEYWORD)
        self.assertEqual(str(kwargs_bound), "**kwargs={'arg5': 5}")

    def test_003_no_value(self):
        params = list(_log_wrap_shared.bind_args_kwargs(sig, 1, arg3=33))
        arg_1_bound = params[0]
        arg1_parameter = arg_1_bound.parameter
        with self.assertRaises(ValueError):
            _log_wrap_shared.BoundParameter(arg1_parameter, arg1_parameter.empty)

    @unittest.skipIf(sys.version_info[:2] < (3, 4), 'python 3 syntax')
    def test_004_annotations(self):
        namespace = {}
        exec("""def func(arg1, arg2: int, arg3: int=3): pass""", namespace)
        func = namespace['func']
        sig = signature(func)
        params = list(_log_wrap_shared.bind_args_kwargs(sig, 1, 2, 4))

        arg_1_bound = params[0]
        self.assertEqual(arg_1_bound.name, 'arg1')
        self.assertEqual(arg_1_bound.value, 1)
        self.assertEqual(arg_1_bound.default, arg_1_bound.empty)
        self.assertEqual(arg_1_bound.annotation, arg_1_bound.empty)
        self.assertEqual(arg_1_bound.kind, arg_1_bound.POSITIONAL_OR_KEYWORD)
        self.assertEqual(str(arg_1_bound), "arg1=1")

        arg_2_bound = params[1]
        self.assertEqual(arg_2_bound.name, 'arg2')
        self.assertEqual(arg_2_bound.value, 2)
        self.assertEqual(arg_2_bound.default, arg_2_bound.empty)
        self.assertEqual(arg_2_bound.annotation, int)
        self.assertEqual(arg_2_bound.kind, arg_2_bound.POSITIONAL_OR_KEYWORD)
        self.assertEqual(str(arg_2_bound), "arg2: int=2")

        arg_3_bound = params[2]
        self.assertEqual(arg_3_bound.name, 'arg3')
        self.assertEqual(arg_3_bound.value, 4)
        self.assertEqual(arg_3_bound.default, 3)
        self.assertEqual(arg_3_bound.annotation, int)
        self.assertEqual(arg_3_bound.kind, arg_3_bound.POSITIONAL_OR_KEYWORD)
        self.assertEqual(str(arg_3_bound), "arg3: int=4  # 3")
