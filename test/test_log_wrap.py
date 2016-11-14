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

import functools
import logging
import sys
import unittest

import logwrap

# pylint: disable=import-error
if sys.version_info.major == 2:
    import mock
else:
    from unittest import mock


@mock.patch('logwrap._log_wrap._logger', autospec=True)
class TestLogWrap(unittest.TestCase):
    def test_no_args(self, logger):
        @logwrap.logwrap
        def func():
            return 'No args'

        result = func()
        self.assertEqual(result, 'No args')
        logger.assert_has_calls((
            mock.call.log(
                level=logging.DEBUG,
                msg="Calling: \n'func'()"
            ),
            mock.call.log(
                level=logging.DEBUG,
                msg="Done: 'func' with result:\n{}".format(
                    logwrap.pretty_repr(result))
            ),
        ))

    def test_args_simple(self, logger):
        arg = 'test arg'

        @logwrap.logwrap
        def func(tst):
            return tst

        result = func(arg)
        self.assertEqual(result, arg)
        logger.assert_has_calls((
            mock.call.log(
                level=logging.DEBUG,
                msg="Calling: \n"
                    "'func'(\n"
                    "    # POSITIONAL_OR_KEYWORD:\n"
                    "    'tst'={},\n"
                    ")".format(
                        logwrap.pretty_repr(
                            arg,
                            indent=8,
                            no_indent_start=True
                        )
                    )
            ),
            mock.call.log(
                level=logging.DEBUG,
                msg="Done: 'func' with result:\n{}".format(
                    logwrap.pretty_repr(result))
            ),
        ))

    def test_args_defaults(self, logger):
        arg = 'test arg'

        @logwrap.logwrap
        def func(tst=arg):
            return tst

        result = func()
        self.assertEqual(result, arg)
        logger.assert_has_calls((
            mock.call.log(
                level=logging.DEBUG,
                msg="Calling: \n"
                    "'func'(\n"
                    "    # POSITIONAL_OR_KEYWORD:\n"
                    "    'tst'={},\n"
                    ")".format(
                        logwrap.pretty_repr(
                            arg,
                            indent=8,
                            no_indent_start=True)
                    )
            ),
            mock.call.log(
                level=logging.DEBUG,
                msg="Done: 'func' with result:\n{}".format(
                    logwrap.pretty_repr(result))
            ),
        ))

    def test_args_complex(self, logger):
        string = 'string'
        dictionary = {'key': 'dictionary'}

        @logwrap.logwrap
        def func(param_string, param_dictionary):
            return param_string, param_dictionary

        result = func(string, dictionary)
        self.assertEqual(result, (string, dictionary))
        # raise ValueError(logger.mock_calls)
        logger.assert_has_calls((
            mock.call.log(
                level=logging.DEBUG,
                msg="Calling: \n"
                    "'func'(\n"
                    "    # POSITIONAL_OR_KEYWORD:\n"
                    "    'param_string'={string},\n"
                    "    'param_dictionary'={dictionary},\n"
                    ")".format(
                        string=logwrap.pretty_repr(
                            string,
                            indent=8, no_indent_start=True),
                        dictionary=logwrap.pretty_repr(
                            dictionary,
                            indent=8, no_indent_start=True)
                    )
            ),
            mock.call.log(
                level=logging.DEBUG,
                msg="Done: 'func' with result:\n{}".format(
                    logwrap.pretty_repr(result))
            ),
        ))

    def test_args_kwargs(self, logger):
        targs = ['string1', 'string2']
        tkwargs = {'key': 'tkwargs'}

        @logwrap.logwrap
        def func(*args, **kwargs):
            return tuple(args), kwargs

        result = func(*targs, **tkwargs)
        self.assertEqual(result, (tuple(targs), tkwargs))
        # raise ValueError(logger.mock_calls)
        logger.assert_has_calls((
            mock.call.log(
                level=logging.DEBUG,
                msg="Calling: \n"
                    "'func'(\n"
                    "    # VAR_POSITIONAL:\n"
                    "    'args'={args},\n"
                    "    # VAR_KEYWORD:\n"
                    "    'kwargs'={kwargs},\n)".format(
                        args=logwrap.pretty_repr(
                            tuple(targs),
                            indent=8, no_indent_start=True),
                        kwargs=logwrap.pretty_repr(
                            tkwargs,
                            indent=8, no_indent_start=True)
                    )
            ),
            mock.call.log(
                level=logging.DEBUG,
                msg="Done: 'func' with result:\n{}".format(
                    logwrap.pretty_repr(result))
            ),
        ))

    def test_renamed_args_kwargs(self, logger):
        arg = 'arg'
        targs = ['string1', 'string2']
        tkwargs = {'key': 'tkwargs'}

        @logwrap.logwrap
        def func(arg, *positional, **named):
            return arg, tuple(positional), named

        result = func(arg, *targs, **tkwargs)
        self.assertEqual(result, (arg, tuple(targs), tkwargs))
        # raise ValueError(logger.mock_calls)
        logger.assert_has_calls((
            mock.call.log(
                level=logging.DEBUG,
                msg="Calling: \n"
                    "'func'(\n"
                    "    # POSITIONAL_OR_KEYWORD:\n"
                    "    'arg'={arg},\n"
                    "    # VAR_POSITIONAL:\n"
                    "    'positional'={args},\n"
                    "    # VAR_KEYWORD:\n"
                    "    'named'={kwargs},\n)".format(
                        arg=logwrap.pretty_repr(
                            arg,
                            indent=8, no_indent_start=True),
                        args=logwrap.pretty_repr(
                            tuple(targs),
                            indent=8, no_indent_start=True),
                        kwargs=logwrap.pretty_repr(
                            tkwargs,
                            indent=8, no_indent_start=True)
                    )
            ),
            mock.call.log(
                level=logging.DEBUG,
                msg="Done: 'func' with result:\n{}".format(
                    logwrap.pretty_repr(result))
            ),
        ))

    def test_negative(self, logger):
        @logwrap.logwrap
        def func():
            raise ValueError('as expected')

        with self.assertRaises(ValueError):
            func()

        logger.assert_has_calls((
            mock.call.log(
                level=logging.DEBUG,
                msg="Calling: \n'func'()"
            ),
            mock.call.log(
                level=logging.ERROR,
                msg="Failed: \n'func'()",
                exc_info=True
            ),
        ))

    def test_negative_substitutions(self, logger):
        new_logger = mock.Mock(spec=logging.Logger, name='logger')
        log = mock.Mock(name='log')
        new_logger.attach_mock(log, 'log')

        @logwrap.logwrap(
            log=new_logger,
            log_level=logging.INFO,
            exc_level=logging.WARNING
        )
        def func():
            raise ValueError('as expected')

        with self.assertRaises(ValueError):
            func()

        self.assertEqual(len(logger.mock_calls), 0)
        log.assert_has_calls((
            mock.call(
                level=logging.INFO,
                msg="Calling: \n'func'()"
            ),
            mock.call(
                level=logging.WARNING,
                msg="Failed: \n'func'()",
                exc_info=True
            ),
        ))

    def test_spec(self, logger):
        new_logger = mock.Mock(spec=logging.Logger, name='logger')
        log = mock.Mock(name='log')
        new_logger.attach_mock(log, 'log')

        arg = 'test arg'

        def spec_func(arg=arg):
            pass

        @logwrap.logwrap(
            log=new_logger,
            spec=spec_func,
        )
        def func(*args, **kwargs):
            return args[0] if args else kwargs.get('arg', arg)

        result = func()
        self.assertEqual(result, arg)
        log.assert_has_calls((
            mock.call(
                level=logging.DEBUG,
                msg="Calling: \n"
                    "'func'(\n"
                    "    # POSITIONAL_OR_KEYWORD:\n"
                    "    'arg'=u'''test arg''',\n"
                    ")"),
            mock.call(
                level=logging.DEBUG,
                msg="Done: 'func' with result:\n"
                    "u'''test arg'''"),
        ))

    def test_indent(self, logger):
        new_logger = mock.Mock(spec=logging.Logger, name='logger')
        log = mock.Mock(name='log')
        new_logger.attach_mock(log, 'log')

        @logwrap.logwrap(log=new_logger, max_indent=10)
        def func():
            return [[[[[[[[[[123]]]]]]]]]]

        func()

        log.assert_has_calls((
            mock.call(
                level=logging.DEBUG,
                msg="Calling: \n"
                    "'func'()"),
            mock.call(
                level=logging.DEBUG,
                msg="Done: 'func' with result:\n"
                    "\n"
                    "list([\n"
                    "    list([\n"
                    "        list([\n"
                    "            [[[[[[[123]]]]]]],\n"
                    "        ]),\n"
                    "    ]),\n"
                    "])"),
        ))

    @unittest.skipUnless(
        sys.version_info[0:2] > (3, 0),
        'Strict python 3 syntax'
    )
    def test_py3_args(self, logger):
        new_logger = mock.Mock(spec=logging.Logger, name='logger')
        log = mock.Mock(name='log')
        new_logger.attach_mock(log, 'log')

        log_call = logwrap.logwrap(log=new_logger)

        namespace = {}

        exec("""
def tst(arg, darg=1, *args, kwarg, dkwarg=4, **kwargs):
    pass
        """,
             namespace
             )
        wrapped = log_call(namespace['tst'])
        wrapped(0, 1, 2, kwarg=3, somekwarg=5)

        log.assert_has_calls((
            mock.call(
                level=logging.DEBUG,
                msg="Calling: \n"
                    "'tst'(\n"
                    "    # POSITIONAL_OR_KEYWORD:\n"
                    "    'arg'=0,\n"
                    "    'darg'=1,\n"
                    "    # VAR_POSITIONAL:\n"
                    "    'args'=\n"
                    "        tuple((\n"
                    "            2,\n"
                    "        )),\n"
                    "    # KEYWORD_ONLY:\n"
                    "    'kwarg'=3,\n"
                    "    'dkwarg'=4,\n"
                    "    # VAR_KEYWORD:\n"
                    "    'kwargs'=\n"
                    "        dict({\n"
                    "            'somekwarg': 5,\n"
                    "        }),\n"
                    ")"),
            mock.call(
                level=logging.DEBUG,
                msg="Done: 'tst' with result:\n"
                    "None"),
        ))

    @unittest.skipUnless(
        sys.version_info[0:2] > (3, 4),
        'Strict python 3.5+ API'
    )
    def test_coroutine(self, logger):

        namespace = {'logwrap': logwrap}

        exec("""
import asyncio

@logwrap.logwrap
async def func():
    pass

loop = asyncio.get_event_loop()
loop.run_until_complete(func())
loop.close()
        """,
             namespace
             )
        # While we're not expanding result coroutine object from namespace,
        # do not check execution result
        logger.assert_has_calls((
            mock.call.log(
                level=logging.DEBUG,
                msg="Calling: \n'func'()"
            ),
        ))

    @unittest.skipUnless(
        sys.version_info[0:2] > (3, 0),
        'Wrap expanding is not supported under python 2.7: funcsigs limitation'
    )
    def test_wrapped(self, logger):
        def simpledeco(func):
            @functools.wraps(func)
            def wrapped(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapped

        @logwrap.logwrap
        @simpledeco
        def func(arg, darg=1, *args, **kwargs):
            return arg, darg, args, kwargs

        result = func(0, 1, 2, arg3=3)
        self.assertEqual(
            result,
            (0, 1, (2, ), {'arg3': 3})
        )
        logger.assert_has_calls((
            mock.call.log(
                level=10,
                msg="Calling: \n"
                    "'func'(\n"
                    "    # POSITIONAL_OR_KEYWORD:\n"
                    "    'arg'=0,\n"
                    "    'darg'=1,\n"
                    "    # VAR_POSITIONAL:\n"
                    "    'args'=\n"
                    "        tuple((\n"
                    "            2,\n"
                    "        )),\n"
                    "    # VAR_KEYWORD:\n"
                    "    'kwargs'=\n"
                    "        dict({\n"
                    "            'arg3': 3,\n"
                    "        }),\n"
                    ")"),
            mock.call.log(
                level=10,
                msg="Done: 'func' with result:\n"
                    "\n"
                    "tuple((\n"
                    "    0,\n"
                    "    1,\n"
                    "    tuple((\n"
                    "        2,\n"
                    "    )),\n"
                    "    dict({\n"
                    "        'arg3': 3,\n"
                    "    }),\n"
                    "))")
        ))
