logwrap
=======

.. image:: https://travis-ci.org/penguinolog/logwrap.svg?branch=master
    :target: https://travis-ci.org/penguinolog/logwrap
.. image:: https://api.codacy.com/project/badge/Grade/72f332d53b924cd2b2c0dc6f9d1f8d0f
    :target: https://www.codacy.com/app/penguinolog/logwrap?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=penguinolog/logwrap&amp;utm_campaign=Badge_Grade

logwrap is a helper for logging in human-readable format function arguments and call result on function call.

This package also includes helpers:

* pretty_repr
* get_arg_names
* get_call_args

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

get_arg_names
-------------
Get argument names for function. This is multiple python versions supporting helper, due to differences between Python 2.7 and Python 3.3+
Usage:

.. code-block:: python

    get_arg_names(func)

where `func` is target function.

get_call_args
-------------
Get call arguments bound to argument names for function. This is multiple python versions supporting helper, due to differences between Python 2.7 and Python 3.5+
Usage:

.. code-block:: python

    get_call_args(func, *positional, **named)

where `func` is target function, `*positional` and `**named` is arguments for the `func`.
Note: get_call_args reqires strictly consistent set of arguments for function.

Testing
=======
The main test mechanism for the package `logwrap` is using `tox`.
Test environments available:

    pep8
    py27
    py34
    py35
    pylint
    docs

Also possible to run `python setup.py test` for unit tests and `python setup.py flake8` for code style tests,
but it requires all package dependencies to be installed.