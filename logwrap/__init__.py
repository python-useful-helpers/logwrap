#    Copyright 2016-2018 Alexey Stepanov aka penguinolog
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
import pkg_resources

from .repr_utils import PrettyFormat, PrettyRepr, PrettyStr, pretty_repr, pretty_str
from .log_wrap import logwrap, LogWrap, BoundParameter, bind_args_kwargs

__all__ = (
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

try:
    __version__ = pkg_resources.get_distribution(__name__).version
except pkg_resources.DistributionNotFound:
    # package is not installed, try to get from SCM
    try:
        import setuptools_scm  # type: ignore

        __version__ = setuptools_scm.get_version()
    except ImportError:
        pass

__author__ = "Alexey Stepanov"
__author_email__ = "penguinolog@gmail.com"
__maintainers__ = {
    "Alexey Stepanov": "penguinolog@gmail.com",
    "Antonio Esposito": "esposito.cloud@gmail.com",
    "Dennis Dmitriev": "dis-xcom@gmail.com",
}
__url__ = "https://github.com/python-useful-helpers/logwrap"
__description__ = "Decorator for logging function arguments and return value by human-readable way"
__license__ = "Apache License, Version 2.0"
