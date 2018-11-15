#    Copyright 2016-2018 Alexey Stepanov aka penguinolog
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

import pkg_resources

from logwrap.repr_utils import PrettyFormat, PrettyRepr, PrettyStr, pretty_repr, pretty_str

from logwrap.log_wrap import LogWrap
from logwrap.log_wrap import logwrap, BoundParameter, bind_args_kwargs

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
)

cpdef str __version__

try:
    __version__ = pkg_resources.get_distribution(__name__).version
except pkg_resources.DistributionNotFound:
    # package is not installed, try to get from SCM
    try:
        import setuptools_scm  # type: ignore

        __version__ = setuptools_scm.get_version()
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
