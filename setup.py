#    Copyright 2016-2021 Alexey Stepanov aka penguinolog

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

# Standard Library
import ast
import distutils.errors
import os.path
import shutil
import sys
import typing
from distutils.command import build_ext

# External Dependencies
import setuptools

try:
    # noinspection PyPackageRequirements
    # External Dependencies
    from Cython.Build import cythonize
except ImportError:
    cythonize = None

PACKAGE_NAME = "logwrap"

with open(os.path.join(os.path.dirname(__file__), PACKAGE_NAME, "__init__.py")) as f:
    SOURCE = f.read()

with open("requirements.txt") as f:
    REQUIRED = f.read().splitlines()

with open("README.rst") as f:
    LONG_DESCRIPTION = f.read()


# noinspection PyCallingNonCallable
if cythonize is not None:
    if "win32" != sys.platform:
        REQUIRES_OPTIMIZATION = [
            setuptools.Extension("logwrap.repr_utils", ["logwrap/repr_utils.pyx"]),
            setuptools.Extension("logwrap.log_wrap", ["logwrap/log_wrap.pyx"]),
        ]
        INTERFACES = ["log_wrap.pxd", "repr_utils.pxd"]
    else:
        REQUIRES_OPTIMIZATION = [
            setuptools.Extension("logwrap.repr_utils", ["logwrap/repr_utils.pyx"]),
        ]
        INTERFACES = ["repr_utils.pxd"]

    EXT_MODULES = cythonize(
        module_list=REQUIRES_OPTIMIZATION,
        compiler_directives={
            "always_allow_keywords": True,
            "binding": True,
            "embedsignature": True,
            "overflowcheck": True,
            "language_level": 3,
        },
    )
else:
    REQUIRES_OPTIMIZATION = []
    INTERFACES = []
    EXT_MODULES = []


class BuildFailed(Exception):
    """For install clear scripts."""


class AllowFailRepair(build_ext.build_ext):
    """This class allows C extension building to fail and repairs init."""

    def run(self) -> None:
        """Run.

        :raises BuildFailed: Build is failed and clean python code should be used.
        """
        try:
            build_ext.build_ext.run(self)

            # Copy __init__.py back to repair package.
            build_dir = os.path.abspath(self.build_lib)
            root_dir = os.path.abspath(os.path.join(__file__, ".."))
            target_dir = build_dir if not self.inplace else root_dir

            src_file = os.path.join(PACKAGE_NAME, "__init__.py")

            src = os.path.join(root_dir, src_file)
            dst = os.path.join(target_dir, src_file)

            if src != dst:
                shutil.copyfile(src, dst)
        except (
            distutils.errors.DistutilsPlatformError,
            FileNotFoundError,
        ):
            raise BuildFailed()

    def build_extension(self, ext) -> None:
        """build_extension.

        :raises BuildFailed: Build is failed and clean python code should be used.
        """
        try:
            build_ext.build_ext.build_extension(self, ext)
        except (
            distutils.errors.CCompilerError,
            distutils.errors.DistutilsExecError,
            distutils.errors.DistutilsPlatformError,
            ValueError,
        ):
            raise BuildFailed()


# noinspection PyUnresolvedReferences
def get_simple_vars_from_src(
    src: str,
) -> "typing.Dict[str, typing.Union[str, bytes, int, float, complex, list, set, dict, tuple, None, bool, Ellipsis]]":
    """Get simple (string/number/boolean and None) assigned values from source.

    :param src: Source code
    :type src: str
    :return: OrderedDict with keys, values = variable names, values
    :rtype: typing.Dict[
                str,
                typing.Union[
                    str, bytes,
                    int, float, complex,
                    list, set, dict, tuple,
                    None, bool, Ellipsis
                ]
            ]

    Limitations: Only defined from scratch variables.
    Not supported by design:
        * Imports
        * Executable code, including string formatting and comprehensions.

    Examples:
    >>> string_sample = "a = '1'"
    >>> get_simple_vars_from_src(string_sample)
    {'a': '1'}

    >>> int_sample = "b = 1"
    >>> get_simple_vars_from_src(int_sample)
    {'b': 1}

    >>> list_sample = "c = [u'1', b'1', 1, 1.0, 1j, None]"
    >>> result = get_simple_vars_from_src(list_sample)
    >>> result == {'c': [u'1', b'1', 1, 1.0, 1j, None]}
    True

    >>> iterable_sample = "d = ([1], {1: 1}, {1})"
    >>> get_simple_vars_from_src(iterable_sample)
    {'d': ([1], {1: 1}, {1})}

    >>> multiple_assign = "e = f = g = 1"
    >>> get_simple_vars_from_src(multiple_assign)
    {'e': 1, 'f': 1, 'g': 1}
    """
    if sys.version_info[:2] < (3, 8):
        ast_data = (ast.Str, ast.Num, ast.List, ast.Set, ast.Dict, ast.Tuple, ast.Bytes, ast.NameConstant, ast.Ellipsis)
    else:
        ast_data = (ast.Constant, ast.List, ast.Set, ast.Dict, ast.Tuple)

    tree = ast.parse(src)

    result = {}

    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast_data):  # We parse assigns only
            continue
        try:
            value = ast.literal_eval(node.value)
        except ValueError:
            continue
        for tgt in node.targets:
            if isinstance(tgt, ast.Name) and isinstance(tgt.ctx, ast.Store):
                result[tgt.id] = value
    return result


VARIABLES = get_simple_vars_from_src(SOURCE)

CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy",
]

KEYWORDS = ["logging", "debugging", "development"]

SETUP_ARGS: typing.Dict[str, typing.Union[str, typing.List[str], typing.Dict[str, typing.List[str]]]] = dict(
    name=PACKAGE_NAME,
    author=VARIABLES["__author__"],
    author_email=VARIABLES["__author_email__"],
    maintainer=", ".join(
        "{name} <{email}>".format(name=name, email=email) for name, email in VARIABLES["__maintainers__"].items()
    ),
    url=VARIABLES["__url__"],
    license=VARIABLES["__license__"],
    description=VARIABLES["__description__"],
    long_description=LONG_DESCRIPTION,
    classifiers=CLASSIFIERS,
    keywords=KEYWORDS,
    python_requires=">=3.7.0",
    # While setuptools cannot deal with pre-installed incompatible versions,
    # setting a lower bound is not harmful - it makes error messages cleaner. DO
    # NOT set an upper bound on setuptools, as that will lead to uninstallable
    # situations as progressive releases of projects are done.
    # Blacklist setuptools 34.0.0-34.3.2 due to https://github.com/pypa/setuptools/issues/951
    # Blacklist setuptools 36.2.0 due to https://github.com/pypa/setuptools/issues/1086
    setup_requires=[
        "setuptools >= 21.0.0,!=24.0.0,"
        "!=34.0.0,!=34.0.1,!=34.0.2,!=34.0.3,!=34.1.0,!=34.1.1,!=34.2.0,!=34.3.0,!=34.3.1,!=34.3.2,"
        "!=36.2.0",
        "wheel",
        "setuptools_scm[toml]>=3.4",
    ],
    use_scm_version={"write_to": f"{PACKAGE_NAME}/_version.py"},
    install_requires=REQUIRED,
    package_data={PACKAGE_NAME: INTERFACES + ["py.typed"]},
)
if cythonize is not None:
    SETUP_ARGS["ext_modules"] = EXT_MODULES
    SETUP_ARGS["cmdclass"] = dict(build_ext=AllowFailRepair)

try:
    setuptools.setup(**SETUP_ARGS)
except BuildFailed:
    print("*" * 80 + "\n* Build Failed!\n* Use clear scripts version.\n" + "*" * 80 + "\n")
    del SETUP_ARGS["ext_modules"]
    del SETUP_ARGS["cmdclass"]
    SETUP_ARGS["package_data"][PACKAGE_NAME] = ["py.typed"]
    setuptools.setup(**SETUP_ARGS)
