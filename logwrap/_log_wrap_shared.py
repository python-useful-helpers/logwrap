#    Copyright 2016-2017 Alexey Stepanov aka penguinolog

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

"""log_wrap shared code module."""

import logging

import logwrap as core

logger = logging.getLogger(__name__)


indent = 4
fmt = "\n{spc:<{indent}}{{key!r}}={{val}},".format(
    spc='',
    indent=indent,
).format
comment = "\n{spc:<{indent}}# {{kind!s}}:".format(spc='', indent=indent).format


def get_func_args_repr(sig, args, kwargs, max_indent, blacklisted_names):
    """Internal helper for reducing complexity of decorator code.

    :type sig: inspect.Signature
    :type args: tuple
    :type kwargs: dict
    :type max_indent: int
    :type blacklisted_names: list
    :rtype: str
    """
    bound = sig.bind(*args, **kwargs).arguments

    param_str = ""

    last_kind = None
    for param in sig.parameters.values():
        if param.name in blacklisted_names:
            continue

        if last_kind != param.kind:
            param_str += comment(kind=param.kind)
            last_kind = param.kind
        param_str += fmt(
            key=param.name,
            val=core.pretty_repr(
                src=bound.get(param.name, param.default),
                indent=indent + 4,
                no_indent_start=True,
                max_indent=max_indent,
            ),
        )
    if param_str:
        param_str += "\n"
    return param_str
