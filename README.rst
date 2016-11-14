logwrap
=======

.. image:: https://travis-ci.org/penguinolog/logwrap.svg?branch=master
    :target: https://travis-ci.org/penguinolog/logwrap
.. image:: https://api.codacy.com/project/badge/Grade/72f332d53b924cd2b2c0dc6f9d1f8d0f
    :target: https://www.codacy.com/app/penguinolog/logwrap?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=penguinolog/logwrap&amp;utm_campaign=Badge_Grade
.. image:: https://api.codacy.com/project/badge/Coverage/72f332d53b924cd2b2c0dc6f9d1f8d0f
    :target: https://www.codacy.com/app/penguinolog/logwrap?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=penguinolog/logwrap&amp;utm_campaign=Badge_Coverage
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

* pretty_repr

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
    )

Limitation: Dict like objects is always marked inside `{}` for readability, even if it is `collections.OrderedDict` (standard repr as list of tuples).

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

Also possible to run `python setup.py test` for unit tests and `python setup.py flake8` for code style tests,
but it requires all package dependencies to be installed.

CI systems
==========
For code checking several CI systems is used in parallel:

1. `Travis CI: <https://travis-ci.org/penguinolog/logwrap>`_ is used for checking: PEP8, pylint, installation possibility and unit tests. Also it's publishes coverage on Codacy.

2. `Codacy: <https://www.codacy.com/app/penguinolog/logwrap/dashboard>`_ is used for statical analysis and coverage display.

CD system
=========
`Travis CI: <https://travis-ci.org/penguinolog/logwrap>`_ is used for package delivery on PyPI.