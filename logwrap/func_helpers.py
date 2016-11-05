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

"""func_helpers module

This is no reason to import this submodule directly, all required methods is
available from the main module.
"""

from __future__ import absolute_import

import collections
import inspect
import sys


# pylint: disable=no-member
def get_arg_names(func):
    """get argument names for function

    :param func: Function to extract arguments from
    :type func: callable
    :return: list of function argument names
    :rtype: list

    >>> def tst_1():
    ...     pass

    >>> get_arg_names(tst_1)
    []

    >>> def tst_2(arg):
    ...     pass

    >>> get_arg_names(tst_2)
    ['arg']
    """
    # noinspection PyUnresolvedReferences
    if sys.version_info[0:2] < (3, 3):
        # pylint: disable=deprecated-method
        # noinspection PyDeprecation
        spec = inspect.getargspec(func=func)
        # pylint: enable=deprecated-method
        args = spec.args[:]
        if spec.varargs:
            args.append(spec.varargs)
        if spec.keywords:
            args.append(spec.keywords)
        return args
    return list(inspect.signature(obj=func).parameters.keys())


def get_call_args(func, *positional, **named):
    """get real function call arguments without calling function

    :param func: Function to bind arguments
    :type func: callable
    :type positional: iterable
    :type named: dict
    :rtype: collections.OrderedDict

    >>> def tst(arg, darg=2, *args, **kwargs):
    ...     pass

    >>> get_call_args(tst, *(1, ))
    OrderedDict([('arg', 1), ('darg', 2), ('args', ()), ('kwargs', {})])
    """
    # noinspection PyUnresolvedReferences
    if sys.version_info[0:2] < (3, 5):  # apply_defaults is py35 feature
        # pylint: disable=deprecated-method
        orig_args = inspect.getcallargs(func, *positional, **named)
        # pylint: enable=deprecated-method
        # Construct OrderedDict as Py3
        arguments = collections.OrderedDict(
            [(key, orig_args[key]) for key in get_arg_names(func)]
        )
        return arguments
    sig = inspect.signature(func).bind(*positional, **named)
    sig.apply_defaults()  # after bind we doesn't have defaults
    return sig.arguments


def get_default_args(func):
    """Get function defaults from it's signature

    :param func: target function
    :type func: function
    :rtype: collections.OrderedDict

    >>> def tst0():pass

    >>> get_default_args(tst0)
    OrderedDict()

    >>> def tst1(a): pass

    >>> get_default_args(tst1)
    OrderedDict()

    >>> def tst2(a, b): pass

    >>> get_default_args(tst2)
    OrderedDict()

    >>> def tst3(a=0): pass

    >>> get_default_args(tst3)
    OrderedDict([('a', 0)])

    >>> def tst4(a, b=1): pass

    >>> get_default_args(tst4)
    OrderedDict([('b', 1)])

    >>> def tst5(a=0, b=1): pass

    >>> get_default_args(tst5)
    OrderedDict([('a', 0), ('b', 1)])
    """
    if sys.version_info[0:2] < (3, 0):
        # pylint: disable=deprecated-method
        # noinspection PyDeprecation
        spec = inspect.getargspec(func)
        # pylint: enable=deprecated-method
        if not spec.defaults:
            return collections.OrderedDict()
        collector = []
        for val in range(1, len(spec.defaults)+1):
            collector.append((spec.args[-val], spec.defaults[-val]))
        return collections.OrderedDict(reversed(collector))
    sig = inspect.signature(func)
    result = collections.OrderedDict(
        [
            (arg.name, arg.default)
            for arg in sig.parameters.values()
            if arg.default != inspect.Parameter.empty
        ]
    )
    return result
# pylint: enable=no-member

__all__ = ['get_arg_names', 'get_call_args']
