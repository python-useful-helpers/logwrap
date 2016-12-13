logwrap
=======

.. image:: https://travis-ci.org/penguinolog/logwrap.svg?branch=master
    :target: https://travis-ci.org/penguinolog/logwrap
.. image:: https://coveralls.io/repos/github/penguinolog/logwrap/badge.svg?branch=master
    :target: https://coveralls.io/github/penguinolog/logwrap?branch=master
.. image:: https://readthedocs.org/projects/logwrap/badge/?version=latest
    :target: http://logwrap.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
.. image:: https://img.shields.io/pypi/v/logwrap.svg
    :target: https://pypi.python.org/pypi/logwrap
.. image:: https://img.shields.io/pypi/pyversions/logwrap.svg
    :target: https://pypi.python.org/pypi/logwrap
.. image:: https://img.shields.io/pypi/status/logwrap.svg
    :target: https://pypi.python.org/pypi/logwrap
.. image:: https://img.shields.io/github/license/penguinolog/logwrap.svg
    :target: https://raw.githubusercontent.com/penguinolog/logwrap/master/LICENSE


logwrap is a helper for logging in human-readable format function arguments and call result on function call.

Pros:

* Free software: Apache license
* Open Source: https://github.com/penguinolog/logwrap
* PyPI packaged: https://pypi.python.org/pypi/logwrap
* Self-documented code: docstrings with types in comments
* Tested: see bages on top
* Support miltiple Python versions:

::

    Python 2.7
    Python 3.4
    Python 3.5
    Python 3.6
    PyPy

This package also includes helpers:

* `pretty_repr`

* `pretty_str`

* `PrettyFormat`

Usage
=====

logwrap
-------
The main decorator. Could be used as not argumented (`@logwrap.logwrap`) and argumented (`@logwrap.logwrap()`).
Not argumented usage simple calls with default values for all positions.
Argumented usage with arguments from signature:

.. code-block:: python

    @logwrap.logwrap(
        log=logging.getLogger(__name__),  # __name__ = 'logwrap'
        log_level=logging.DEBUG,
        exc_level=logging.ERROR,
        max_indent=20,  # forwarded to the pretty_repr
        spec=None,  # use target callable function for spec
    )

Usage examples:

.. code-block:: python

    @logwrap.logwrap()
    def foo():
        pass

is equal to:

.. code-block:: python

    @logwrap.logwrap
    def foo():
        pass

Get decorator for use without parameters:

.. code-block:: python

    get_logs = logwap.logwrap()  # set required parameters via arguments

    @get_logs
    def foo():
        pass

Limitations:
* return value from awaitable objects (`async def(...`) is not accessible - on call asyncio object is returned.

* nested wrapping (`@logwrap @deco2 ...`) is not parsed under python 2.7: `funcsigs` limitation. Please set `logwrap` as the first level decorator.

pretty_repr
-----------
This is specified helper for making human-readable repr on complex objects.
Signature is self-documenting:

.. code-block:: python

    def pretty_repr(
        src,  # object for repr
        indent=0,  # start indent
        no_indent_start=False,  # do not indent the first level
        max_indent=20,  # maximum allowed indent level
        indent_step=4,  # step between indents
        py2_str=False,  # use bytes for python 2 __repr__ and __str__
    )

Limitation: Dict like objects is always marked inside `{}` for readability, even if it is `collections.OrderedDict` (standard repr as list of tuples).

pretty_str
----------
This is specified helper for making human-readable str on complex objects.
Signature is self-documenting:

.. code-block:: python

    def pretty_str(
        src,  # object for __str__
        indent=0,  # start indent
        no_indent_start=False,  # do not indent the first level
        max_indent=20,  # maximum allowed indent level
        indent_step=4,  # step between indents
        py2_str=False,  # use bytes for python 2 __repr__ and __str__
    )

Limitations:
    Dict like objects is always marked inside `{}` for readability, even if it is `collections.OrderedDict` (standard repr as list of tuples).

    Iterable types is not declared, only brackets is used.

    String and bytes looks the same (its __str__, not __repr__).

PrettyFormat
------------
PrettyFormat is the main formatting implementation class. on `pretty_repr` instance of this class is created and executed.
Object signature:

.. code-block:: python

    def __init__(
        self,
        simple_formatters,  # Will be used to repr not complex. Keys is data types and 'default'.
        complex_formatters,  # Currently only legacy pretty_repr formatters is supported, will be extended in the future
        keyword='repr',  # Currently 'repr' is supported, will be extended in the future
        max_indent=20,  # maximum allowed indent level
        indent_step=4,  # step between indents
        py2_str=False,  # use bytes for python 2 __repr__ and __str__
    )

Callable object (`PrettyFormat` instance) signature:

.. code-block:: python

    def __call__(
        self,
        src,  # object for repr
        indent=0,  # start indent
        no_indent_start=False  # do not indent the first level
    )

Adopting your code
------------------
pretty_repr behavior could be overridden for your classes by implementing specific magic method:

.. code-block:: python

    def __pretty_repr__(
        self,
        parser  # PrettyFormat class instance,
        indent  # start indent,
        no_indent_start  # do not indent the first level
    ):
        return ...

This method will be executed instead of __repr__ on your object.

Testing
=======
The main test mechanism for the package `logwrap` is using `tox`.
Test environments available:

::

    pep8
    py27
    py34
    py35
    pypy
    pylint
    docs

CI systems
==========
For code checking several CI systems is used in parallel:

1. `Travis CI: <https://travis-ci.org/penguinolog/logwrap>`_ is used for checking: PEP8, pylint, bandit, installation possibility and unit tests. Also it's publishes coverage on coveralls.

2. `coveralls: <https://coveralls.io/github/penguinolog/logwrap>`_ is used for coverage display.

CD system
=========
`Travis CI: <https://travis-ci.org/penguinolog/logwrap>`_ is used for package delivery on PyPI.
