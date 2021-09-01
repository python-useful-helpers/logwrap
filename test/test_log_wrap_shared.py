#    Copyright 2018 - 2021 Alexey Stepanov aka penguinolog

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

# Standard Library
import unittest
from inspect import signature

# Package Implementation
from logwrap import log_wrap


def example_function(arg1, arg2: int = 2, *args, arg3, arg4: int = 4, **kwargs) -> None:
    """Function to use as signature source."""


sig = signature(example_function)


# noinspection PyUnusedLocal,PyMissingOrEmptyDocstring
class TestBind(unittest.TestCase):
    def test_001_positive(self):
        params = list(log_wrap.bind_args_kwargs(sig, 1, arg3=33))
        arg_1_bound = params[0]
        self.assertEqual(arg_1_bound.name, "arg1")
        self.assertEqual(arg_1_bound.value, 1)
        self.assertEqual(arg_1_bound.default, arg_1_bound.empty)
        self.assertEqual(arg_1_bound.annotation, arg_1_bound.empty)
        self.assertEqual(arg_1_bound.kind, arg_1_bound.POSITIONAL_OR_KEYWORD)
        self.assertEqual(str(arg_1_bound), "arg1=1")

        arg_2_bound = params[1]
        self.assertEqual(arg_2_bound.name, "arg2")
        self.assertEqual(arg_2_bound.value, 2)
        self.assertEqual(arg_2_bound.default, 2)
        self.assertEqual(arg_2_bound.annotation, int)
        self.assertEqual(arg_2_bound.kind, arg_2_bound.POSITIONAL_OR_KEYWORD)
        self.assertEqual(str(arg_2_bound), "arg2: int=2  # 2")

        args_bound = params[2]
        self.assertEqual(args_bound.name, "args")
        self.assertEqual(args_bound.value, args_bound.empty)
        self.assertEqual(args_bound.default, args_bound.empty)
        self.assertEqual(args_bound.annotation, args_bound.empty)
        self.assertEqual(args_bound.kind, args_bound.VAR_POSITIONAL)
        self.assertEqual(str(args_bound), "*args=()")

        arg_3_bound = params[3]
        self.assertEqual(arg_3_bound.name, "arg3")
        self.assertEqual(arg_3_bound.value, 33)
        self.assertEqual(arg_3_bound.default, arg_3_bound.empty)
        self.assertEqual(arg_3_bound.annotation, arg_3_bound.empty)
        self.assertEqual(arg_3_bound.kind, arg_3_bound.KEYWORD_ONLY)
        self.assertEqual(str(arg_3_bound), "arg3=33")

        arg_4_bound = params[4]
        self.assertEqual(arg_4_bound.name, "arg4")
        self.assertEqual(arg_4_bound.value, 4)
        self.assertEqual(arg_4_bound.default, 4)
        self.assertEqual(arg_4_bound.annotation, int)
        self.assertEqual(arg_4_bound.kind, arg_4_bound.KEYWORD_ONLY)
        self.assertEqual(str(arg_4_bound), "arg4: int=4  # 4")

        kwargs_bound = params[5]
        self.assertEqual(kwargs_bound.name, "kwargs")
        self.assertEqual(kwargs_bound.value, kwargs_bound.empty)
        self.assertEqual(kwargs_bound.default, kwargs_bound.empty)
        self.assertEqual(kwargs_bound.annotation, kwargs_bound.empty)
        self.assertEqual(kwargs_bound.kind, kwargs_bound.VAR_KEYWORD)
        self.assertEqual(str(kwargs_bound), "**kwargs={}")

    def test_002_args_kwargs(self):
        params = list(log_wrap.bind_args_kwargs(sig, 1, 2, 3, arg3=30, arg4=40, arg5=50))

        args_bound = params[2]
        self.assertEqual(args_bound.name, "args")
        self.assertEqual(args_bound.value, (3,))
        self.assertEqual(args_bound.default, args_bound.empty)
        self.assertEqual(args_bound.annotation, args_bound.empty)
        self.assertEqual(args_bound.kind, args_bound.VAR_POSITIONAL)
        self.assertEqual(str(args_bound), "*args=(3,)")

        kwargs_bound = params[5]
        self.assertEqual(kwargs_bound.name, "kwargs")
        self.assertEqual(kwargs_bound.value, {"arg5": 50})
        self.assertEqual(kwargs_bound.default, kwargs_bound.empty)
        self.assertEqual(kwargs_bound.annotation, kwargs_bound.empty)
        self.assertEqual(kwargs_bound.kind, kwargs_bound.VAR_KEYWORD)
        self.assertEqual(str(kwargs_bound), "**kwargs={'arg5': 50}")

    def test_003_no_value(self):
        params = list(log_wrap.bind_args_kwargs(sig, 1, arg3=33))
        arg_1_bound = params[0]
        arg1_parameter = arg_1_bound
        with self.assertRaises(ValueError):
            log_wrap.BoundParameter(arg1_parameter, arg1_parameter.empty)

    def test_004_annotations(self):
        def func(arg1, arg2: int, arg3: int = 3):
            pass

        sig = signature(func)
        params = list(log_wrap.bind_args_kwargs(sig, 1, 2, 4))

        arg_1_bound = params[0]
        self.assertEqual(arg_1_bound.name, "arg1")
        self.assertEqual(arg_1_bound.value, 1)
        self.assertEqual(arg_1_bound.default, arg_1_bound.empty)
        self.assertEqual(arg_1_bound.annotation, arg_1_bound.empty)
        self.assertEqual(arg_1_bound.kind, arg_1_bound.POSITIONAL_OR_KEYWORD)
        self.assertEqual(str(arg_1_bound), "arg1=1")

        arg_2_bound = params[1]
        self.assertEqual(arg_2_bound.name, "arg2")
        self.assertEqual(arg_2_bound.value, 2)
        self.assertEqual(arg_2_bound.default, arg_2_bound.empty)
        self.assertEqual(arg_2_bound.annotation, int)
        self.assertEqual(arg_2_bound.kind, arg_2_bound.POSITIONAL_OR_KEYWORD)
        self.assertEqual(str(arg_2_bound), "arg2: int=2")

        arg_3_bound = params[2]
        self.assertEqual(arg_3_bound.name, "arg3")
        self.assertEqual(arg_3_bound.value, 4)
        self.assertEqual(arg_3_bound.default, 3)
        self.assertEqual(arg_3_bound.annotation, int)
        self.assertEqual(arg_3_bound.kind, arg_3_bound.POSITIONAL_OR_KEYWORD)
        self.assertEqual(str(arg_3_bound), "arg3: int=4  # 3")
