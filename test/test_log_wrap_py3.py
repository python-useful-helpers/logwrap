#    Copyright 2016 - 2018 Alexey Stepanov aka penguinolog

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

"""Python 3 specific tests"""

import asyncio
import io
import logging
import typing  # noqa # pylint: disable=unused-import
import unittest
from unittest import mock

import logwrap


# noinspection PyUnusedLocal,PyMissingOrEmptyDocstring
class TestLogWrapAsync(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loop = asyncio.get_event_loop()

    def setUp(self):
        """Preparation for tests.

        Due to no possibility of proper mock patch of function defaults, modify directly.
        """
        self.logger = logging.getLogger('logwrap')
        self.logger.setLevel(logging.DEBUG)

        self.stream = io.StringIO()

        self.logger.handlers.clear()
        handler = logging.StreamHandler(self.stream)
        handler.setFormatter(logging.Formatter(fmt='%(levelname)s>%(message)s'))
        self.logger.addHandler(handler)

    def tearDown(self):
        """Revert modifications."""
        self.logger.handlers.clear()

    def test_coroutine_async(self):
        @logwrap.logwrap
        @asyncio.coroutine
        def func():
            pass

        self.loop.run_until_complete(func())
        self.assertEqual(
            "DEBUG>Awaiting: \n"
            "'func'()\n"
            "DEBUG>Done: 'func' with result:\n"
            "None\n",
            self.stream.getvalue(),
        )

    def test_coroutine_async_as_argumented(self):
        new_logger = mock.Mock(spec=logging.Logger, name='logger')
        log = mock.Mock(name='log')
        new_logger.attach_mock(log, 'log')

        @logwrap.logwrap(log=new_logger)
        @asyncio.coroutine
        def func():
            pass

        self.loop.run_until_complete(func())

        self.assertEqual(
            [
                mock.call.log(
                    level=logging.DEBUG,
                    msg="Awaiting: \n'func'()"
                ),
                mock.call.log(
                    level=logging.DEBUG,
                    msg="Done: 'func' with result:\nNone"
                )
            ],
            log.mock_calls,
        )

    def test_coroutine_fail(self):
        @logwrap.logwrap
        @asyncio.coroutine
        def func():
            raise Exception('Expected')

        with self.assertRaises(Exception):
            self.loop.run_until_complete(func())

        self.assertEqual(
            'DEBUG>Awaiting: \n'
            "'func'()\n"
            'ERROR>Failed: \n'
            "'func'()\n"
            'Traceback (most recent call last):',
            '\n'.join(self.stream.getvalue().split('\n')[:5]),
        )

    def test_exceptions_blacklist(self):
        new_logger = mock.Mock(spec=logging.Logger, name='logger')
        log = mock.Mock(name='log')
        new_logger.attach_mock(log, 'log')

        @logwrap.logwrap(log=new_logger, blacklisted_exceptions=[TypeError])
        @asyncio.coroutine
        def func():
            raise TypeError('Blacklisted')

        with self.assertRaises(TypeError):
            self.loop.run_until_complete(func())

        # While we're not expanding result coroutine object from namespace,
        # do not check execution result

        self.assertEqual(
            [
                mock.call(
                    level=logging.DEBUG,
                    msg="Awaiting: \n'func'()"
                ),
            ],
            log.mock_calls,
        )


# noinspection PyUnusedLocal,PyMissingOrEmptyDocstring
class TestAnnotated(unittest.TestCase):
    def setUp(self):
        """Preparation for tests.

        Due to no possibility of proper mock patch of function defaults, modify directly.
        """
        self.logger = logging.getLogger('logwrap')
        self.logger.setLevel(logging.DEBUG)

        self.stream = io.StringIO()

        self.logger.handlers.clear()
        handler = logging.StreamHandler(self.stream)
        handler.setFormatter(logging.Formatter(fmt='%(levelname)s>%(message)s'))
        self.logger.addHandler(handler)

    def tearDown(self):
        """Revert modifications."""
        self.logger.handlers.clear()

    def test_annotation_args(self):
        @logwrap.logwrap
        def func(a: typing.Optional[int] = None):
            pass

        func()
        self.assertEqual(
            "DEBUG>Calling: \n"
            "'func'(\n"
            "    # POSITIONAL_OR_KEYWORD:\n"
            "    'a'=None,  # type: typing.Union[int, NoneType]\n"
            ")\n"
            "DEBUG>Done: 'func' with result:\n"
            "None\n",
            self.stream.getvalue(),
        )
