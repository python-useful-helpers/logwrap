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

# pylint: disable=missing-docstring, unused-argument, no-self-argument, no-self-use, keyword-arg-before-vararg

"""Python independent logwrap tests."""

# Standard Library
import functools
import io
import logging
import unittest
from unittest import mock

# LogWrap Implementation
import logwrap


class AnyStringWith(str):
    def __eq__(self, other):
        return self in other


# noinspection PyUnusedLocal,PyMissingOrEmptyDocstring
class TestLogWrap(unittest.TestCase):
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

    def test_001_no_args(self):
        @logwrap.logwrap
        def func():
            return 'No args'

        result = func()
        self.assertEqual(result, 'No args')

        self.assertEqual(
            f"DEBUG>Calling: \n"
            f"'func'()\n"
            f"DEBUG>Done: 'func' with result:\n"
            f"{logwrap.pretty_repr(result)}\n",
            self.stream.getvalue(),
        )

    def test_002_args_simple(self):
        arg = 'test arg'

        @logwrap.logwrap
        def func(tst):
            return tst

        result = func(arg)
        self.assertEqual(result, arg)
        self.assertEqual(
            f"DEBUG>Calling: \n"
            f"'func'(\n"
            f"    # POSITIONAL_OR_KEYWORD:\n"
            f"    'tst'={logwrap.pretty_repr(arg, indent=8, no_indent_start=True)},\n"
            f")\n"
            f"DEBUG>Done: 'func' with result:\n"
            f"{logwrap.pretty_repr(result)}\n",
            self.stream.getvalue(),
        )

    def test_003_args_defaults(self):
        arg = 'test arg'

        @logwrap.logwrap
        def func(tst=arg):
            return tst

        result = func()
        self.assertEqual(result, arg)

        self.assertEqual(
            f"DEBUG>Calling: \n"
            f"'func'(\n"
            f"    # POSITIONAL_OR_KEYWORD:\n"
            f"    'tst'={logwrap.pretty_repr(arg, indent=8, no_indent_start=True)},\n"
            f")\n"
            f"DEBUG>Done: 'func' with result:\n"
            f"{logwrap.pretty_repr(result)}\n",
            self.stream.getvalue(),
        )

    def test_004_args_complex(self):
        arg1 = 'arg1'
        arg2 = 'arg2'

        @logwrap.logwrap
        def func(arg_1, arg_2):
            return arg_1, arg_2

        result = func(arg1, arg2)
        self.assertEqual(result, (arg1, arg2))

        self.assertEqual(
            f"DEBUG>Calling: \n"
            f"'func'(\n"
            f"    # POSITIONAL_OR_KEYWORD:\n"
            f"    'arg_1'={logwrap.pretty_repr(arg1, indent=8, no_indent_start=True)},\n"
            f"    'arg_2'={logwrap.pretty_repr(arg2, indent=8, no_indent_start=True)},\n"
            f")\n"
            f"DEBUG>Done: 'func' with result:\n"
            f"{logwrap.pretty_repr(result)}\n",
            self.stream.getvalue(),
        )

    def test_005_args_kwargs(self):
        targs = ['string1', 'string2']
        tkwargs = {'key': 'tkwargs'}

        @logwrap.logwrap
        def func(*args, **kwargs):
            return tuple(args), kwargs

        result = func(*targs, **tkwargs)
        self.assertEqual(result, (tuple(targs), tkwargs))

        self.assertEqual(
            f"DEBUG>Calling: \n"
            f"'func'(\n"
            f"    # VAR_POSITIONAL:\n"
            f"    'args'={logwrap.pretty_repr(tuple(targs), indent=8, no_indent_start=True)},\n"
            f"    # VAR_KEYWORD:\n"
            f"    'kwargs'={logwrap.pretty_repr(tkwargs, indent=8, no_indent_start=True)},\n"
            f")\n"
            f"DEBUG>Done: 'func' with result:\n"
            f"{logwrap.pretty_repr(result)}\n",
            self.stream.getvalue(),
        )

    def test_006_renamed_args_kwargs(self):
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
            f"DEBUG>Calling: \n"
            f"'func'(\n"
            f"    # POSITIONAL_OR_KEYWORD:\n"
            f"    'arg'={logwrap.pretty_repr(arg, indent=8, no_indent_start=True)},\n"
            f"    # VAR_POSITIONAL:\n"
            f"    'positional'={logwrap.pretty_repr(tuple(targs), indent=8, no_indent_start=True)},\n"
            f"    # VAR_KEYWORD:\n"
            f"    'named'={logwrap.pretty_repr(tkwargs, indent=8, no_indent_start=True)},\n"
            f")\n"
            f"DEBUG>Done: 'func' with result:\n"
            f"{logwrap.pretty_repr(result)}\n",
            self.stream.getvalue(),
        )

    def test_007_negative(self):
        @logwrap.logwrap
        def func():
            raise ValueError('as expected')

        with self.assertRaises(ValueError):
            func()

        self.assertEqual(
            'DEBUG>Calling: \n'
            "'func'()\n"
            'ERROR>Failed: \n'
            "'func'()\n"
            'Traceback (most recent call last):',
            '\n'.join(self.stream.getvalue().split('\n')[:5]),
        )

    def test_008_negative_substitutions(self):
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

        self.assertEqual(
            [
                mock.call(
                    level=logging.INFO,
                    msg="Calling: \n'func'()"
                ),
                mock.call(
                    level=logging.WARNING,
                    msg=AnyStringWith("Failed: \n'func'()"),
                    exc_info=False
                ),
            ],
            log.mock_calls,
        )

    def test_009_spec(self):
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
            [
                mock.call(
                    level=logging.DEBUG,
                    msg=f"Calling: \n"
                        f"'func'(\n"
                        f"    # POSITIONAL_OR_KEYWORD:\n"
                        f"    'arg'={logwrap.pretty_repr(arg, indent=8, no_indent_start=True)},\n"
                        f")"),
                mock.call(
                    level=logging.DEBUG,
                    msg=f"Done: 'func' with result:\n"
                        f"{logwrap.pretty_repr(result)}"),
            ],
            log.mock_calls,
        )

    def test_010_indent(self):
        new_logger = mock.Mock(spec=logging.Logger, name='logger')
        log = mock.Mock(name='log')
        new_logger.attach_mock(log, 'log')

        @logwrap.logwrap(log=new_logger, max_indent=10)
        def func():
            return [[[[[[[[[[123]]]]]]]]]]

        result = func()

        self.assertEqual(
            [
                mock.call(
                    level=logging.DEBUG,
                    msg="Calling: \n"
                        "'func'()"),
                mock.call(
                    level=logging.DEBUG,
                    msg=f"Done: 'func' with result:\n"
                        f"{logwrap.pretty_repr(result, max_indent=10)}"),
            ],
            log.mock_calls,
        )

    def test_011_method(self):
        class Tst:
            @logwrap.logwrap
            def func(tst_self):
                return 'No args'

            def __repr__(tst_self):
                return '<Tst_instance>'

        tst = Tst()
        result = tst.func()
        self.assertEqual(result, 'No args')
        self.assertEqual(
            f"DEBUG>Calling: \n"
            f"'func'(\n"
            f"    # POSITIONAL_OR_KEYWORD:\n"
            f"    'tst_self'={logwrap.pretty_repr(tst)},\n"
            f")\n"
            f"DEBUG>Done: 'func' with result:\n"
            f"{logwrap.pretty_repr(result)}\n",
            self.stream.getvalue(),
        )

    def test_012_class_decorator(self):
        @logwrap.LogWrap
        def func():
            return 'No args'

        result = func()
        self.assertEqual(result, 'No args')
        self.assertEqual(
            f"DEBUG>Calling: \n"
            f"'func'()\n"
            f"DEBUG>Done: 'func' with result:\n"
            f"{logwrap.pretty_repr(result)}\n",
            self.stream.getvalue(),
        )

    def test_013_py3_args(self):
        new_logger = mock.Mock(spec=logging.Logger, name='logger')
        log = mock.Mock(name='log')
        new_logger.attach_mock(log, 'log')

        log_call = logwrap.logwrap(log=new_logger)

        def tst(arg, darg=1, *args, kwarg, dkwarg=4, **kwargs):
            pass

        wrapped = log_call(tst)
        wrapped(0, 1, 2, kwarg=3, somekwarg=5)

        self.assertEqual(
            log.mock_calls,
            [
                mock.call(
                    level=logging.DEBUG,
                    msg=f"Calling: \n"
                        f"'tst'(\n"
                        f"    # POSITIONAL_OR_KEYWORD:\n"
                        f"    'arg'=0,\n"
                        f"    'darg'=1,\n"
                        f"    # VAR_POSITIONAL:\n"
                        f"    'args'={logwrap.pretty_repr((2,), indent=8, no_indent_start=True)},\n"
                        f"    # KEYWORD_ONLY:\n"
                        f"    'kwarg'=3,\n"
                        f"    'dkwarg'=4,\n"
                        f"    # VAR_KEYWORD:\n"
                        f"    'kwargs'={logwrap.pretty_repr(dict(somekwarg=5), indent=8, no_indent_start=True)},\n"
                        f")"),
                mock.call(
                    level=logging.DEBUG,
                    msg="Done: 'tst' with result:\n"
                        "None"),
            ]
        )

    def test_014_wrapped(self):
        # noinspection PyShadowingNames
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
        self.assertEqual(
            f"DEBUG>Calling: \n"
            f"'func'(\n"
            f"    # POSITIONAL_OR_KEYWORD:\n"
            f"    'arg'=0,\n"
            f"    'darg'=1,\n"
            f"    # VAR_POSITIONAL:\n"
            f"    'args'={logwrap.pretty_repr((2, ), indent=8, no_indent_start=True)},\n"
            f"    # VAR_KEYWORD:\n"
            f"    'kwargs'={logwrap.pretty_repr(dict(arg3=3), indent=8, no_indent_start=True)},\n"
            f")\n"
            f"DEBUG>Done: 'func' with result:\n"
            f"{logwrap.pretty_repr(result)}\n",
            self.stream.getvalue(),
        )

    def test_015_args_blacklist(self):
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
                        f"Calling: \n"
                        f"'func'(\n"
                        f"    # POSITIONAL_OR_KEYWORD:\n"
                        f"    'test_arg1'={logwrap.pretty_repr(arg1, indent=8, no_indent_start=True)},\n"
                        f")"
                    )
                ),
                mock.call(
                    level=logging.DEBUG,
                    msg="Done: 'func' with result:\n{}".format(
                        logwrap.pretty_repr(result))
                ),
            ]
        )

    def test_016_exceptions_blacklist(self):
        new_logger = mock.Mock(spec=logging.Logger, name='logger')
        log = mock.Mock(name='log')
        new_logger.attach_mock(log, 'log')

        @logwrap.logwrap(log=new_logger, blacklisted_exceptions=[TypeError])
        def func():
            raise TypeError('Blacklisted')

        with self.assertRaises(TypeError):
            func()

        self.assertEqual(
            [
                mock.call(
                    level=logging.DEBUG,
                    msg="Calling: \n'func'()"
                ),
            ],
            log.mock_calls,
        )

    def test_017_disable_args(self):
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
            ],
            log.mock_calls,
        )

    def test_018_disable_args_exc(self):
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

        self.assertEqual(
            [
                mock.call(
                    level=logging.DEBUG,
                    msg=(
                        f"Calling: \n"
                        f"'func'(\n"
                        f"    # POSITIONAL_OR_KEYWORD:\n"
                        f"    'test_arg1'={logwrap.pretty_repr(arg1, indent=8, no_indent_start=True)},\n"
                        f"    'test_arg2'={logwrap.pretty_repr(arg2, indent=8, no_indent_start=True)},\n"
                        f")"
                    )
                ),
                mock.call(
                    level=logging.ERROR,
                    msg=AnyStringWith("Failed: \n'func'()"),
                    exc_info=False
                ),
            ],
            log.mock_calls,
        )

    def test_019_disable_all_args(self):
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

        self.assertEqual(
            [
                mock.call(
                    level=logging.DEBUG,
                    msg="Calling: \n"
                        "'func'()"
                ),
                mock.call(
                    level=logging.ERROR,
                    msg=AnyStringWith("Failed: \n'func'()"),
                    exc_info=False
                ),
            ],
            log.mock_calls,
        )

    def test_020_disable_result(self):
        new_logger = mock.Mock(spec=logging.Logger, name='logger')
        log = mock.Mock(name='log')
        new_logger.attach_mock(log, 'log')

        @logwrap.logwrap(log=new_logger, log_result_obj=False)
        def func():
            return 'not logged'

        func()

        self.assertEqual(
            [
                mock.call(
                    level=logging.DEBUG,
                    msg="Calling: \n'func'()"
                ),
                mock.call(
                    level=logging.DEBUG,
                    msg="Done: 'func'"
                ),
            ],
            log.mock_calls,
        )

    def test_021_empty_args_kwargs(self):
        @logwrap.logwrap
        def func(*args, **kwargs):
            return 'No args'

        result = func()
        self.assertEqual(result, 'No args')
        self.assertEqual(
            f"DEBUG>Calling: \n"
            f"'func'(\n"
            f"    # VAR_POSITIONAL:\n"
            f"    'args'=(),\n"
            f"    # VAR_KEYWORD:\n"
            f"    'kwargs'={{}},\n"
            f")\n"
            f"DEBUG>Done: 'func' with result:\n"
            f"{logwrap.pretty_repr(result)}\n",
            self.stream.getvalue(),
        )

    def test_022_disable_traceback(self):
        new_logger = mock.Mock(spec=logging.Logger, name='logger')
        log = mock.Mock(name='log')
        new_logger.attach_mock(log, 'log')

        @logwrap.logwrap(
            log=new_logger,
            log_traceback=False
        )
        def func():
            raise TypeError('Blacklisted')

        with self.assertRaises(TypeError):
            func()

        self.assertEqual(
            [
                mock.call(
                    level=logging.DEBUG,
                    msg="Calling: \n"
                        "'func'()"
                ),
                mock.call(
                    level=logging.ERROR,
                    msg=AnyStringWith("Failed: \n'func'()"),
                    exc_info=False
                ),
            ],
            log.mock_calls,
        )
        self.assertNotEqual(
            mock.call(
                level=logging.ERROR,
                msg=AnyStringWith("Failed: \n'func'()\nTraceback (most recent call last):"),
                exc_info=False
            ),
            log.mock_calls[1],
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
        self.assertTrue(log_call.log_traceback)
        self.assertTrue(log_call.log_result_obj)

        log_call.log_level = logging.INFO
        log_call.exc_level = logging.CRITICAL
        log_call.max_indent = 40
        log_call.blacklisted_names.append('password')
        log_call.blacklisted_exceptions.append(IOError)
        log_call.log_call_args = False
        log_call.log_call_args_on_exc = False
        log_call.log_traceback = False
        log_call.log_result_obj = False

        self.assertEqual(log_call.log_level, logging.INFO)
        self.assertEqual(log_call.exc_level, logging.CRITICAL)
        self.assertEqual(log_call.max_indent, 40)
        self.assertEqual(log_call.blacklisted_names, ['password'])
        self.assertEqual(log_call.blacklisted_exceptions, [IOError])
        self.assertFalse(log_call.log_call_args)
        self.assertFalse(log_call.log_call_args_on_exc)
        self.assertFalse(log_call.log_traceback)
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
