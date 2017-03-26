.. PrettyFormat, pretty_repr and pretty_str

API: Helpers: `pretty_repr`, `pretty_str` and base class `PrettyFormat`.
========================================================================

.. py:module:: logwrap
.. py:currentmodule:: logwrap

.. py:function:: pretty_repr(src, indent=0, no_indent_start=False, max_indent=20, indent_step=4, py2_str=False, )

    Make human readable repr of object.

    :param src: object to process
    :type src: typing.Union[
               six.binary_type, six.text_type, int, typing.Iterable, object
               ]
    :param indent: start indentation, all next levels is +indent_step
    :type indent: int
    :param no_indent_start: do not indent open bracket and simple parameters
    :type no_indent_start: bool
    :param max_indent: maximal indent before classic repr() call
    :type max_indent: int
    :param indent_step: step for the next indentation level
    :type indent_step: int
    :param py2_str: use Python 2.x compatible strings instead of unicode
    :type py2_str: bool
    :return: formatted string
    :rtype: str


.. py:function:: pretty_str(src, indent=0, no_indent_start=False, max_indent=20, indent_step=4, py2_str=False, )

    Make human readable str of object.

    .. versionadded:: 1.1.0

    :param src: object to process
    :type src: typing.Union[
               six.binary_type, six.text_type, int, typing.Iterable, object
               ]
    :param indent: start indentation, all next levels is +indent_step
    :type indent: int
    :param no_indent_start: do not indent open bracket and simple parameters
    :type no_indent_start: bool
    :param max_indent: maximal indent before classic repr() call
    :type max_indent: int
    :param indent_step: step for the next indentation level
    :type indent_step: int
    :param py2_str: use Python 2.x compatible strings instead of unicode
    :type py2_str: bool
    :return: formatted string
    :rtype: str


.. py:class:: PrettyFormat(simple_formatters, complex_formatters, keyword='repr', max_indent=20, indent_step=4, py2_str=False, )

    Designed for usage as __repr__ and __str__ replacement on complex objects

    .. versionadded:: 1.0.2

    :param simple_formatters: object formatters by type
    :type simple_formatters: typing.Dict[str, types.FunctionType]
    :param complex_formatters: object formatters for complex objects
    :type complex_formatters: typing.Dict[str, types.FunctionType]
    :param keyword: operation keyword (__pretty_{keyword}__)
    :type keyword: str
    :param max_indent: maximal indent before classic repr() call
    :type max_indent: int
    :param indent_step: step for the next indentation level
    :type indent_step: int
    :param py2_str: use Python 2.x compatible strings instead of unicode
    :type py2_str: bool

    .. note:: Attributes is read-only

    .. py:attribute:: max_indent

    .. py:attribute:: indent_step

    .. py:method:: next_indent(indent, multiplier=1)

        Next indentation value. Used internally and on __pretty_{keyword}__ calls.

        :param indent: current indentation value
        :type indent: int
        :param multiplier: step multiplier
        :type multiplier: int
        :rtype: int

    .. py:method:: process_element(src, indent=0, no_indent_start=False)

        Make human readable representation of object.

        :param src: object to process
        :type src: typing.Union[
                   six.binary_type, six.text_type, int, typing.Iterable, object
                   ]
        :param indent: start indentation
        :type indent: int
        :param no_indent_start:
            do not indent open bracket and simple parameters
        :type no_indent_start: bool
        :return: formatted string
        :rtype: six.text_type

    .. py:method:: __call__(src, indent=0, no_indent_start=False)

        Make human readable representation of object. The main entry point.

        :param src: object to process
        :type src: typing.Union[
                   six.binary_type, six.text_type, int, typing.Iterable, object
                   ]
        :param indent: start indentation
        :type indent: int
        :param no_indent_start:
            do not indent open bracket and simple parameters
        :type no_indent_start: bool
        :return: formatted string
        :rtype: str
