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

"""logwrap decorator for human-readable logging of command arguments"""

import setuptools

import logwrap

with open('README.rst') as f:
    long_description = f.read()

setuptools.setup(
    name='logwrap',
    version=logwrap.__version__,
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',

        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: Jython',
    ],
    keywords='logging debugging development',

    zip_safe=True,
    url='https://github.com/penguinolog/logwrap',
    license='Apache License, Version 2.0',
    author='Alexey Stepanov',
    author_email='penguinolog@gmail.com',
    description=(
        'Decorator for logging function arguments by human-readable way'
    ),
    long_description=long_description,
    install_requires=['six'],
    extras_require={
        ':python_version == "2.7"': [
            'funcsigs>=1.0',
        ],
        ':python_version == "3.4"': [
            'typing>=3.5',
        ],
    },
)
