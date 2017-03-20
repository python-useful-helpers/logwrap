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

"""logwrap module.

Contents: 'logwrap', 'pretty_repr', 'pretty_str'

Original code was made for Mirantis Inc by Alexey Stepanov,
later it has been reworked and extended for support of special cases.
"""

from __future__ import absolute_import

import six

from ._log_wrap import logwrap, LogWrap
from ._repr_utils import PrettyFormat, pretty_repr, pretty_str

__version__ = '2.2.1'

__all__ = (
    'logwrap',
    'PrettyFormat',
    'pretty_repr',
    'pretty_str'
)

# pylint: disable=ungrouped-imports, no-name-in-module
if six.PY34:
    from ._alogwrap import async_logwrap, AsyncLogWrap

    __all__ += ('async_logwrap', 'AsyncLogWrap')
# pylint: enable=ungrouped-imports, no-name-in-module
