#    Copyright 2018 - 2020 Alexey Stepanov aka penguinolog
##
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

from logwrap.repr_utils import PrettyFormat, PrettyRepr, PrettyStr, pretty_repr, pretty_str

from logwrap.log_wrap import LogWrap
from logwrap.log_wrap import logwrap, BoundParameter, bind_args_kwargs

from logwrap.log_on_access import LogOnAccess

cpdef tuple __all__ = (
    "LogWrap",
    "logwrap",
    "PrettyFormat",
    "PrettyRepr",
    "PrettyStr",
    "pretty_repr",
    "pretty_str",
    "BoundParameter",
    "bind_args_kwargs",
    "LogOnAccess",
)

cpdef str __version__

try:
    from ._version import version as __version__
except ImportError:
    pass

cpdef str __author__ = "Alexey Stepanov"
cpdef str __author_email__ = "penguinolog@gmail.com"
cpdef dict __maintainers__ = {
    "Alexey Stepanov": "penguinolog@gmail.com",
    "Antonio Esposito": "esposito.cloud@gmail.com",
    "Dennis Dmitriev": "dis-xcom@gmail.com",
}
cpdef str __url__ = "https://github.com/python-useful-helpers/logwrap"
cpdef str __description__ = "Decorator for logging function arguments and return value by human-readable way"
cpdef str __license__ = "Apache License, Version 2.0"
