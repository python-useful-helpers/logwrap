#    Copyright 2016 - 2018 Alexey Stepanov aka penguinolog

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

"""Python independent logwrap tests."""

from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import unittest

import six

import logwrap

# pylint: disable=import-error
if six.PY2:
    # noinspection PyUnresolvedReferences
    import mock
else:
    from unittest import mock


# noinspection PyUnusedLocal,PyMissingOrEmptyDocstring
@mock.patch('logwrap._log_wrap_shared.logger', autospec=True)
class TestLogWrap(unittest.TestCase):
    def test_001_no_args(self, logger):
        @logwrap.logwrap
        def func():
            return 'No args'

        result = func()
        self.assertEqual(result, 'No args')
        self.assertEqual(
            logger.mock_calls,
            [
                mock.call.log(
                    level=logging.DEBUG,
                    msg="Calling: \n'func'()"
                ),
                mock.call.log(
                    level=logging.DEBUG,
                    msg="Done: 'func' with result:\n{}".format(
                        logwrap.pretty_repr(result))
                ),
            ]
        )

    def test_002_args_simple(self, logger):
        arg = 'test arg'

        @logwrap.logwrap
        def func(tst):
            return tst

        result = func(arg)
        self.assertEqual(result, arg)
        self.assertEqual(
            logger.mock_calls,
            [
                mock.call.log(
                    level=logging.DEBUG,
                    msg=(
                        "Calling: \n"
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
                    )
                ),
                mock.call.log(
                    level=logging.DEBUG,
                    msg="Done: 'func' with result:\n{}".format(
                        logwrap.pretty_repr(result))
                ),
            ]
        )

    def test_003_args_defaults(self, logger):
        arg = 'test arg'

        @logwrap.logwrap
        def func(tst=arg):
            return tst

        result = func()
        self.assertEqual(result, arg)

        self.assertEqual(
            logger.mock_calls,
            [
                mock.call.log(
                    level=logging.DEBUG,
                    msg=(
                        "Calling: \n"
                        "'func'(\n"
                        "    # POSITIONAL_OR_KEYWORD:\n"
                        "    'tst'={},\n"
                        ")".format(
                            logwrap.pretty_repr(
                                arg,
                                indent=8,
                                no_indent_start=True)
                        )
                    )
                ),
                mock.call.log(
                    level=logging.DEBUG,
                    msg="Done: 'func' with result:\n{}".format(
                        logwrap.pretty_repr(result))
                ),
            ]
        )

    def test_004_args_complex(self, logger):
        string = 'string'
        dictionary = {'key': 'dictionary'}

        @logwrap.logwrap
        def func(param_string, param_dictionary):
            return param_string, param_dictionary

        result = func(string, dictionary)
        self.assertEqual(result, (string, dictionary))

        self.assertEqual(
            logger.mock_calls,
            [
                mock.call.log(
                    level=logging.DEBUG,
                    msg=(
                        "Calling: \n"
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
                    )
                ),
                mock.call.log(
                    level=logging.DEBUG,
                    msg="Done: 'func' with result:\n{}".format(
                        logwrap.pretty_repr(result))
                ),
            ]
        )

    def test_005_args_kwargs(self, logger):
        targs = ['string1', 'string2']
        tkwargs = {'key': 'tkwargs'}

        @logwrap.logwrap
        def func(*args, **kwargs):
            return tuple(args), kwargs

        result = func(*targs, **tkwargs)
        self.assertEqual(result, (tuple(targs), tkwargs))

        self.assertEqual(
            logger.mock_calls,
            [
                mock.call.log(
                    level=logging.DEBUG,
                    msg=(
                        "Calling: \n"
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
                    )
                ),
                mock.call.log(
                    level=logging.DEBUG,
                    msg="Done: 'func' with result:\n{}".format(
                        logwrap.pretty_repr(result))
                ),
            ]
        )

    def test_006_renamed_args_kwargs(self, logger):
        arg = 'arg'
        targs = ['string1', 'string2']
        tkwargs = {'key': 'tkwargs'}

        # noinspection PyShadowingNames
        @logwrap.logwrap
        def func(arg, *positional, **named):
            return arg, tuple(positional), named

        result = func(arg, *targs, **tkwargs)
        self.assertEqual(result, (arg, tuple(targs), tkwargs))
        self.assertEqual(
            logger.mock_calls,
            [
                mock.call.log(
                    level=logging.DEBUG,
                    msg=(
                        "Calling: \n"
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
                    )
                ),
                mock.call.log(
                    level=logging.DEBUG,
                    msg="Done: 'func' with result:\n{}".format(
                        logwrap.pretty_repr(result))
                ),
            ]
        )

    def test_007_negative(self, logger):
        @logwrap.logwrap
        def func():
            raise ValueError('as expected')

        with self.assertRaises(ValueError):
            func()

        self.assertEqual(
            logger.mock_calls,
            [
                mock.call.log(
                    level=logging.DEBUG,
                    msg="Calling: \n'func'()"
                ),
                mock.call.log(
                    level=logging.ERROR,
                    msg="Failed: \n'func'()",
                    exc_info=True
                ),
            ]
        )

    def test_008_negative_substitutions(self, logger):
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
        self.assertEqual(
            log.mock_calls,
            [
                mock.call(
                    level=logging.INFO,
                    msg="Calling: \n'func'()"
                ),
                mock.call(
                    level=logging.WARNING,
                    msg="Failed: \n'func'()",
                    exc_info=True
                ),
            ]
        )

    def test_009_spec(self, logger):
        new_logger = mock.Mock(spec=logging.Logger, name='logger')
        log = mock.Mock(name='log')
        new_logger.attach_mock(log, 'log')

        arg = 'test arg'

        # noinspection PyShadowingNames
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
        self.assertEqual(
            log.mock_calls,
            [
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
            ]
        )

    def test_010_indent(self, logger):
        new_logger = mock.Mock(spec=logging.Logger, name='logger')
        log = mock.Mock(name='log')
        new_logger.attach_mock(log, 'log')

        @logwrap.logwrap(log=new_logger, max_indent=10)
        def func():
            return [[[[[[[[[[123]]]]]]]]]]

        func()

        self.assertEqual(
            log.mock_calls,
            [
                mock.call(
                    level=logging.DEBUG,
                    msg="Calling: \n"
                        "'func'()"),
                mock.call(
                    level=logging.DEBUG,
                    msg="Done: 'func' with result:\n"
                        "list([\n"
                        "    list([\n"
                        "        list([\n"
                        "            [[[[[[[123]]]]]]],\n"
                        "        ]),\n"
                        "    ]),\n"
                        "])"),
            ]
        )

    def test_011_method(self, logger):
        class Tst(object):
            @logwrap.logwrap
            def func(tst_self):
                return 'No args'

            def __repr__(tst_self):
                return '<Tst_instance>'

        tst = Tst()
        result = tst.func()
        self.assertEqual(result, 'No args')
        self.assertEqual(
            logger.mock_calls,
            [
                mock.call.log(
                    level=logging.DEBUG,
                    msg="Calling: \n"
                        "'func'(\n"
                        "    # POSITIONAL_OR_KEYWORD:\n"
                        "    'tst_self'=<Tst_instance>,\n"
                        ")"
                ),
                mock.call.log(
                    level=logging.DEBUG,
                    msg="Done: 'func' with result:\n{}".format(
                        logwrap.pretty_repr(result))
                ),
            ]
        )

    def test_012_class_decorator(self, logger):
        @logwrap.LogWrap
        def func():
            return 'No args'

        result = func()
        self.assertEqual(result, 'No args')
        self.assertEqual(
            logger.mock_calls,
            [
                mock.call.log(
                    level=logging.DEBUG,
                    msg="Calling: \n'func'()"
                ),
                mock.call.log(
                    level=logging.DEBUG,
                    msg="Done: 'func' with result:\n{}".format(
                        logwrap.pretty_repr(result))
                ),
            ]
        )

    @unittest.skipUnless(
        six.PY3,
        'Strict python 3 syntax'
    )
    def test_013_py3_args(self, logger):
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

        self.assertEqual(
            log.mock_calls,
            [
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
            ]
        )

    def test_014_wrapped(self, logger):
        # noinspection PyShadowingNames
        def simpledeco(func):
            @six.wraps(func)
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
        self.assertEqual(
            logger.mock_calls,
            [
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
            ]
        )

    def test_015_args_blacklist(self, logger):
        new_logger = mock.Mock(spec=logging.Logger, name='logger')
        log = mock.Mock(name='log')
        new_logger.attach_mock(log, 'log')

        arg1 = 'test arg 1'
        arg2 = 'test arg 2'

        @logwrap.logwrap(log=new_logger, blacklisted_names=['test_arg2'])
        def func(test_arg1, test_arg2):
            return test_arg1, test_arg2

        result = func(arg1, arg2)
        self.assertEqual(result, (arg1, arg2))
        self.assertEqual(
            log.mock_calls,
            [
                mock.call(
                    level=logging.DEBUG,
                    msg=(
                        "Calling: \n"
                        "'func'(\n"
                        "    # POSITIONAL_OR_KEYWORD:\n"
                        "    'test_arg1'={},\n"
                        ")".format(
                            logwrap.pretty_repr(
                                arg1,
                                indent=8,
                                no_indent_start=True
                            )
                        )
                    )
                ),
                mock.call(
                    level=logging.DEBUG,
                    msg="Done: 'func' with result:\n{}".format(
                        logwrap.pretty_repr(result))
                ),
            ]
        )

    def test_016_exceptions_blacklist(self, logger):
        new_logger = mock.Mock(spec=logging.Logger, name='logger')
        log = mock.Mock(name='log')
        new_logger.attach_mock(log, 'log')

        @logwrap.logwrap(log=new_logger, blacklisted_exceptions=[TypeError])
        def func():
            raise TypeError('Blacklisted')

        with self.assertRaises(TypeError):
            func()

        self.assertEqual(len(logger.mock_calls), 0)
        self.assertEqual(
            log.mock_calls,
            [
                mock.call(
                    level=logging.DEBUG,
                    msg="Calling: \n'func'()"
                ),
            ]
        )

    def test_017_disable_args(self, logger):
        new_logger = mock.Mock(spec=logging.Logger, name='logger')
        log = mock.Mock(name='log')
        new_logger.attach_mock(log, 'log')

        arg1 = 'test arg 1'
        arg2 = 'test arg 2'

        @logwrap.logwrap(log=new_logger, log_call_args=False)
        def func(test_arg1, test_arg2):
            return test_arg1, test_arg2

        result = func(arg1, arg2)
        self.assertEqual(result, (arg1, arg2))
        self.assertEqual(
            log.mock_calls,
            [
                mock.call(
                    level=logging.DEBUG,
                    msg="Calling: \n"
                        "'func'()"
                ),
                mock.call(
                    level=logging.DEBUG,
                    msg="Done: 'func' with result:\n{}".format(
                        logwrap.pretty_repr(result))
                ),
            ]
        )

    def test_018_disable_args_exc(self, logger):
        new_logger = mock.Mock(spec=logging.Logger, name='logger')
        log = mock.Mock(name='log')
        new_logger.attach_mock(log, 'log')

        arg1 = 'test arg 1'
        arg2 = 'test arg 2'

        @logwrap.logwrap(log=new_logger, log_call_args_on_exc=False)
        def func(test_arg1, test_arg2):
            raise TypeError('Blacklisted')

        with self.assertRaises(TypeError):
            func(arg1, arg2)

        self.assertEqual(len(logger.mock_calls), 0)
        self.assertEqual(
            log.mock_calls,
            [
                mock.call(
                    level=logging.DEBUG,
                    msg=(
                        "Calling: \n"
                        "'func'(\n"
                        "    # POSITIONAL_OR_KEYWORD:\n"
                        "    'test_arg1'={},\n"
                        "    'test_arg2'={},\n"
                        ")".format(
                            logwrap.pretty_repr(
                                arg1,
                                indent=8,
                                no_indent_start=True
                            ),
                            logwrap.pretty_repr(
                                arg2,
                                indent=8,
                                no_indent_start=True
                            ),
                        )
                    )
                ),
                mock.call(
                    level=logging.ERROR,
                    msg="Failed: \n'func'()",
                    exc_info=True
                ),
            ]
        )

    def test_019_disable_all_args(self, logger):
        new_logger = mock.Mock(spec=logging.Logger, name='logger')
        log = mock.Mock(name='log')
        new_logger.attach_mock(log, 'log')

        arg1 = 'test arg 1'
        arg2 = 'test arg 2'

        @logwrap.logwrap(
            log=new_logger,
            log_call_args=False,
            log_call_args_on_exc=False
        )
        def func(test_arg1, test_arg2):
            raise TypeError('Blacklisted')

        with self.assertRaises(TypeError):
            func(arg1, arg2)

        self.assertEqual(len(logger.mock_calls), 0)
        self.assertEqual(
            log.mock_calls,
            [
                mock.call(
                    level=logging.DEBUG,
                    msg="Calling: \n"
                        "'func'()"
                ),
                mock.call(
                    level=logging.ERROR,
                    msg="Failed: \n'func'()",
                    exc_info=True
                ),
            ]
        )

    def test_020_disable_result(self, logger):
        new_logger = mock.Mock(spec=logging.Logger, name='logger')
        log = mock.Mock(name='log')
        new_logger.attach_mock(log, 'log')

        @logwrap.logwrap(log=new_logger, log_result_obj=False)
        def func():
            return 'not logged'

        func()

        self.assertEqual(len(logger.mock_calls), 0)
        self.assertEqual(
            log.mock_calls,
            [
                mock.call(
                    level=logging.DEBUG,
                    msg="Calling: \n'func'()"
                ),
                mock.call(
                    level=logging.DEBUG,
                    msg="Done: 'func'"
                ),
            ]
        )


class TestObject(unittest.TestCase):
    def test_001_basic(self):
        log_call = logwrap.LogWrap()
        self.assertEqual(log_call.log_level, logging.DEBUG)
        self.assertEqual(log_call.exc_level, logging.ERROR)
        self.assertEqual(log_call.max_indent, 20)
        self.assertEqual(log_call.blacklisted_names, [])
        self.assertEqual(log_call.blacklisted_exceptions, [])
        self.assertTrue(log_call.log_call_args)
        self.assertTrue(log_call.log_call_args_on_exc)
        self.assertTrue(log_call.log_result_obj)

        log_call.log_level = logging.INFO
        log_call.exc_level = logging.CRITICAL
        log_call.max_indent = 40
        log_call.blacklisted_names.append('password')
        log_call.blacklisted_exceptions.append(IOError)
        log_call.log_call_args = False
        log_call.log_call_args_on_exc = False
        log_call.log_result_obj = False

        self.assertEqual(log_call.log_level, logging.INFO)
        self.assertEqual(log_call.exc_level, logging.CRITICAL)
        self.assertEqual(log_call.max_indent, 40)
        self.assertEqual(log_call.blacklisted_names, ['password'])
        self.assertEqual(log_call.blacklisted_exceptions, [IOError])
        self.assertFalse(log_call.log_call_args)
        self.assertFalse(log_call.log_call_args_on_exc)
        self.assertFalse(log_call.log_result_obj)

        with self.assertRaises(TypeError):
            log_call.log_level = 'WARNING'

        self.assertEqual(
            '{cls}('
            'log={logger}, '
            'log_level={obj.log_level}, '
            'exc_level={obj.exc_level}, '
            'max_indent={obj.max_indent}, '
            'spec=None, '
            'blacklisted_names={obj.blacklisted_names}, '
            'blacklisted_exceptions={obj.blacklisted_exceptions}, '
            'log_call_args={obj.log_call_args}, '
            'log_call_args_on_exc={obj.log_call_args_on_exc}, '
            'log_result_obj={obj.log_result_obj}, '
            ')'.format(
                cls=log_call.__class__.__name__,
                logger=log_call._logger,
                obj=log_call
            ),
            repr(log_call),
        )

    def test_002_override_skip_arg(self):
        class SkipArg(logwrap.LogWrap):
            def pre_process_param(
                self,
                arg,
            ):
                if 'skip' in arg.name:
                    return None
                return arg

        log = mock.Mock(spec=logging.Logger, name='logger')

        wrapper = SkipArg(log=log, log_result_obj=False)

        @wrapper
        def func(arg, arg_skip, arg2=None, skip_arg=None):
            pass

        func(1, 2)
        self.assertEqual(
            log.mock_calls,
            [
                mock.call.log(
                    level=logging.DEBUG,
                    msg="Calling: \n"
                        "'func'(\n"
                        "    # POSITIONAL_OR_KEYWORD:\n"
                        "    'arg'=1,\n"
                        "    'arg2'=None,\n"
                        ")"),
                mock.call.log(level=logging.DEBUG, msg="Done: 'func'")
            ]
        )

    def test_003_override_change_arg(self):
        class ChangeArg(logwrap.LogWrap):
            def pre_process_param(
                self,
                arg,
            ):
                if 'secret' in arg.name:
                    return arg, None
                return arg

        log = mock.Mock(spec=logging.Logger, name='logger')

        wrapper = ChangeArg(log=log, log_result_obj=False)

        @wrapper
        def func(arg, arg_secret, arg2='public', secret_arg=('key')):
            pass

        func('data', 'key')
        self.assertEqual(
            log.mock_calls,
            [
                mock.call.log(
                    level=logging.DEBUG,
                    msg="Calling: \n"
                        "'func'(\n"
                        "    # POSITIONAL_OR_KEYWORD:\n"
                        "    'arg'=u'''data''',\n"
                        "    'arg_secret'=None,\n"
                        "    'arg2'=u'''public''',\n"
                        "    'secret_arg'=None,\n"
                        ")"),
                mock.call.log(level=logging.DEBUG, msg="Done: 'func'")
            ]
        )

    def test_003_override_change_repr(self):
        class ChangeRepr(logwrap.LogWrap):
            def post_process_param(
                self,
                arg,
                arg_repr
            ):
                if 'secret' in arg.name:
                    return "<*hidden*>"
                return arg_repr

        log = mock.Mock(spec=logging.Logger, name='logger')

        wrapper = ChangeRepr(log=log, log_result_obj=False)

        @wrapper
        def func(arg, arg_secret, arg2='public', secret_arg=('key')):
            pass

        func('data', 'key')
        self.assertEqual(
            log.mock_calls,
            [
                mock.call.log(
                    level=logging.DEBUG,
                    msg="Calling: \n"
                        "'func'(\n"
                        "    # POSITIONAL_OR_KEYWORD:\n"
                        "    'arg'=u'''data''',\n"
                        "    'arg_secret'=<*hidden*>,\n"
                        "    'arg2'=u'''public''',\n"
                        "    'secret_arg'=<*hidden*>,\n"
                        ")"),
                mock.call.log(level=logging.DEBUG, msg="Done: 'func'")
            ]
        )


# noinspection PyUnusedLocal,PyMissingOrEmptyDocstring
@mock.patch('logwrap._log_wrap_shared.logger', autospec=True)
class TestDeprecation(unittest.TestCase):
    def test_001_args_func(self, logger):
        new_logger = mock.Mock(spec=logging.Logger, name='logger')
        log = mock.Mock(name='log')
        new_logger.attach_mock(log, 'log')

        arg = 'test arg'

        with mock.patch('warnings.warn') as warn:
            @logwrap.logwrap(
                new_logger,
            )
            def func(*args, **kwargs):
                return args[0] if args else kwargs.get('arg', arg)

            self.assertTrue(bool(warn.mock_calls))

        result = func()
        self.assertEqual(result, arg)
        self.assertEqual(
            log.mock_calls,
            [
                mock.call(
                    level=logging.DEBUG,
                    msg="Calling: \n"
                        "'func'(\n"
                        "    # VAR_POSITIONAL:\n"
                        "    'args'=(),\n"
                        "    # VAR_KEYWORD:\n"
                        "    'kwargs'={},\n"
                        ")"),
                mock.call(
                    level=logging.DEBUG,
                    msg="Done: 'func' with result:\n"
                        "u'''test arg'''"),
            ]
        )

    def test_002_args_cls(self, logger):
        new_logger = mock.Mock(spec=logging.Logger, name='logger')
        log = mock.Mock(name='log')
        new_logger.attach_mock(log, 'log')

        arg = 'test arg'

        with mock.patch('warnings.warn') as warn:
            @logwrap.LogWrap(
                new_logger,
            )
            def func(*args, **kwargs):
                return args[0] if args else kwargs.get('arg', arg)

            self.assertTrue(bool(warn.mock_calls))

        result = func()
        self.assertEqual(result, arg)
        self.assertEqual(
            log.mock_calls,
            [
                mock.call(
                    level=logging.DEBUG,
                    msg="Calling: \n"
                        "'func'(\n"
                        "    # VAR_POSITIONAL:\n"
                        "    'args'=(),\n"
                        "    # VAR_KEYWORD:\n"
                        "    'kwargs'={},\n"
                        ")"),
                mock.call(
                    level=logging.DEBUG,
                    msg="Done: 'func' with result:\n"
                        "u'''test arg'''"),
            ]
        )
