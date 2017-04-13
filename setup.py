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

"""logwrap decorator for human-readable logging of command arguments."""

import setuptools

setuptools.setup(
    name='logwrap',
    extras_require={
        ':python_version == "2.7"': [
            'funcsigs>=1.0',
        ],
        ':python_version <= "3.4"': [
            'typing>=3.5',
        ],
        ':python_version == "3.3"': [
            'asyncio>=3.4',
        ],
    },
)
