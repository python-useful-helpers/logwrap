#    Copyright 2016 - 2021 Alexey Stepanov aka penguinolog

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

# pylint: disable=unused-argument

"""Python 3 specific tests."""

from __future__ import annotations

import io
import logging
import unittest

import logwrap


# noinspection PyUnusedLocal,PyMissingOrEmptyDocstring
class TestAnnotated(unittest.TestCase):
    def setUp(self):
        """Prepare for tests.

        Due to no possibility of proper mock patch of function defaults, modify directly.
        """
        self.logger = logging.getLogger("logwrap")
        self.logger.setLevel(logging.DEBUG)

        self.stream = io.StringIO()

        self.logger.handlers.clear()
        handler = logging.StreamHandler(self.stream)
        handler.setFormatter(logging.Formatter(fmt="%(levelname)s>%(message)s"))
        self.logger.addHandler(handler)

    def tearDown(self):
        """Revert modifications."""
        self.logger.handlers.clear()

    def test_01_annotation_args(self):
        @logwrap.logwrap
        def func(arg: int | None = None):
            pass

        func()
        self.assertEqual(
            "DEBUG>Calling: \n"
            "func(\n"
            "    # POSITIONAL_OR_KEYWORD:\n"
            "    arg=None,  # type: int | None\n"
            ")\n"
            "DEBUG>Done: 'func' with result:\n"
            "None\n",
            self.stream.getvalue(),
        )

    def test_02_annotation_args(self):
        @logwrap.logwrap
        def func(arg: int = 0):
            pass

        func()
        self.assertEqual(
            "DEBUG>Calling: \n"
            "func(\n"
            "    # POSITIONAL_OR_KEYWORD:\n"
            "    arg=0,  # type: int\n"
            ")\n"
            "DEBUG>Done: 'func' with result:\n"
            "None\n",
            self.stream.getvalue(),
        )
