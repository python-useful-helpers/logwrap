#    Copyright 2016-2017 Alexey Stepanov aka penguinolog
#
#    Copyright 2016 Mirantis, Inc.
#
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

"""logwrap module.

Contents: 'logwrap', 'pretty_repr', 'pretty_str'

Original code was made for Mirantis Inc by Alexey Stepanov,
later it has been reworked and extended for support of special cases.
"""

from __future__ import absolute_import

import sys

from ._repr_utils import (
    PrettyFormat,
    PrettyRepr,
    PrettyStr,
    pretty_repr,
    pretty_str
)

PY3 = sys.version_info[:2] > (3, 0)

# pylint: disable=no-name-in-module
if PY3:  # pragma: no cover
    from ._log_wrap3 import logwrap, LogWrap
else:  # pragma: no cover
    from ._log_wrap2 import logwrap, LogWrap
# pylint: enable=no-name-in-module

__all__ = (
    'LogWrap',
    'logwrap',
    'PrettyFormat',
    'PrettyRepr',
    'PrettyStr',
    'pretty_repr',
    'pretty_str'
)

__version__ = '3.1.0'
__author__ = "Alexey Stepanov"
__author_email__ = 'penguinolog@gmail.com'
__url__ = 'https://github.com/penguinolog/logwrap'
__description__ = (
    "Decorator for logging function arguments and "
    "return value by human-readable way"
)
__license__ = "Apache License, Version 2.0"
