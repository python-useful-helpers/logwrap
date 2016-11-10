.. _getstart:

Getting Started
===============

logwrap is a python package with several helpers, primary designed for easy
logging of function calls by human-readable way.

There are several functions are made public for usage in external code:

* logwrap - decorator for logging of function calls

* pretty_repr - helpers for making human-readable repr output for complex objects

Every helper contains docstring with description for call arguments.
There is no reason for importing any submodule: the all public API is exposed on the top level.

Example of code (Python 3 related)
**********************************

.. code-block:: python

   import logwrap

   @logwrap.logwrap
   def example_function1(
           arg1: str,
           arg2: str='arg2',
           *args,
           kwarg1: str,
           kwarg2: str='kwarg2',
           **kwargs
   ) -> tuple():
       return (arg1, arg2, args, kwarg1, kwarg2, kwargs)

   example_function1('arg1', kwarg1='kwarg1', kwarg3='kwarg3')

This code during execution will produce log records:

::

    Calling:
    'example_function1'(
        # POSITIONAL_OR_KEYWORD:
        'arg1'=u'''arg1''',
        'arg2'=u'''arg2''',
        # VAR_POSITIONAL:
        'args'=(),
        # KEYWORD_ONLY:
        'kwarg1'=u'''kwarg1''',
        'kwarg2'=u'''kwarg2''',
        # VAR_KEYWORD:
        'kwargs'=
             dict({
                'kwarg3': u'''kwarg3''',
             }),
    )
    Done: 'example_function1' with result:

     tuple((
        u'''arg1''',
        u'''arg2''',
        (),
        u'''kwarg1''',
        u'''kwarg2''',
         dict({
            'kwarg3': u'''kwarg3''',
         }),
     ))

During execution of function `pretty_repr` is called for every argument and call result.

.. code-block:: python

    pretty_repr(('arg1', 'arg2', (), 'kwarg1', 'kwarg2', {'kwarg3': 'kwarg3'})

