#    Copyright 2016 - 2017 Alexey Stepanov aka penguinolog

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

"""Python 3 specific tests"""

try:
    import asyncio
except ImportError:
    asyncio = None
import logging
import sys
import unittest
try:
    from unittest import mock
except ImportError:
    # noinspection PyUnresolvedReferences
    import mock

import logwrap


# noinspection PyUnusedLocal,PyMissingOrEmptyDocstring
@mock.patch('logwrap._log_wrap_shared.logger', autospec=True)
@unittest.skipIf(
    asyncio is None or sys.version_info[:2] < (3, 5),
    'Strict python 3.5+ API'
)
class TestLogWrapAsync(unittest.TestCase):
    """async def differs from asyncio.coroutine."""
    @classmethod
    def setUpClass(cls):
        cls.loop = asyncio.get_event_loop()

    def test_coroutine_async(self, logger):
        namespace = {'logwrap': logwrap}

        exec("""
@logwrap.logwrap
async def func():
    pass
                """,
             namespace
             )
        func = namespace['func']

        self.loop.run_until_complete(func())
        self.assertEqual(
            logger.mock_calls,
            [
                mock.call.log(
                    level=logging.DEBUG,
                    msg="Awaiting: \n'func'()"
                ),
                mock.call.log(
                    level=logging.DEBUG,
                    msg="Done: 'func' with result:\nNone"
                )
            ]
        )

    def test_coroutine_async_as_argumented(self, logger):
        new_logger = mock.Mock(spec=logging.Logger, name='logger')
        log = mock.Mock(name='log')
        new_logger.attach_mock(log, 'log')

        namespace = {'logwrap': logwrap, 'new_logger': new_logger}

        exec("""
@logwrap.logwrap(log=new_logger)
async def func():
    pass
                        """,
             namespace
             )
        func = namespace['func']

        self.loop.run_until_complete(func())

        self.assertEqual(
            log.mock_calls,
            [
                mock.call.log(
                    level=logging.DEBUG,
                    msg="Awaiting: \n'func'()"
                ),
                mock.call.log(
                    level=logging.DEBUG,
                    msg="Done: 'func' with result:\nNone"
                )
            ]
        )

    def test_coroutine_fail(self, logger):
        namespace = {'logwrap': logwrap}

        exec("""
@logwrap.logwrap
async def func():
    raise Exception('Expected')
                                """,
             namespace
             )
        func = namespace['func']

        with self.assertRaises(Exception):
            self.loop.run_until_complete(func())

        self.assertEqual(
            logger.mock_calls,
            [
                mock.call.log(
                    level=logging.DEBUG,
                    msg="Awaiting: \n'func'()"
                ),
                mock.call.log(
                    level=logging.ERROR,
                    msg="Failed: \n'func'()",
                    exc_info=True
                )
            ]
        )

    def test_exceptions_blacklist(self, logger):
        new_logger = mock.Mock(spec=logging.Logger, name='logger')
        log = mock.Mock(name='log')
        new_logger.attach_mock(log, 'log')

        namespace = {'logwrap': logwrap, 'new_logger': new_logger}

        exec("""
@logwrap.logwrap(log=new_logger, blacklisted_exceptions=[TypeError])
async def func():
    raise TypeError('Blacklisted')
                                """,
             namespace
             )
        func = namespace['func']

        with self.assertRaises(TypeError):
            self.loop.run_until_complete(func())

        # While we're not expanding result coroutine object from namespace,
        # do not check execution result

        self.assertEqual(len(logger.mock_calls), 0)
        self.assertEqual(
            log.mock_calls,
            [
                mock.call(
                    level=logging.DEBUG,
                    msg="Awaiting: \n'func'()"
                ),
            ]
        )
