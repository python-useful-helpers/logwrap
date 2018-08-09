.. PrettyFormat, pretty_repr and pretty_str

API: Helpers: `pretty_repr`, `pretty_str` and base class `PrettyFormat`.
========================================================================

.. py:module:: logwrap
.. py:currentmodule:: logwrap

.. py:function:: pretty_repr(src, indent=0, no_indent_start=False, max_indent=20, indent_step=4, )

    Make human readable repr of object.

    :param src: object to process
    :type src: typing.Any
    :param indent: start indentation, all next levels is +indent_step
    :type indent: int
    :param no_indent_start: do not indent open bracket and simple parameters
    :type no_indent_start: bool
    :param max_indent: maximal indent before classic repr() call
    :type max_indent: int
    :param indent_step: step for the next indentation level
    :type indent_step: int
    :return: formatted string
    :rtype: str


.. py:function:: pretty_str(src, indent=0, no_indent_start=False, max_indent=20, indent_step=4, )

    Make human readable str of object.

    .. versionadded:: 1.1.0

    :param src: object to process
    :type src: typing.Any
    :param indent: start indentation, all next levels is +indent_step
    :type indent: int
    :param no_indent_start: do not indent open bracket and simple parameters
    :type no_indent_start: bool
    :param max_indent: maximal indent before classic repr() call
    :type max_indent: int
    :param indent_step: step for the next indentation level
    :type indent_step: int
    :return: formatted string
    :rtype: str


.. py:class:: PrettyFormat(object)

    Designed for usage as __repr__ and __str__ replacement on complex objects

    .. versionadded:: 1.0.2
    .. versionchanged:: 3.0.1

    .. py:method:: __init__(max_indent=20, indent_step=4, )

        :param max_indent: maximal indent before classic repr() call
        :type max_indent: int
        :param indent_step: step for the next indentation level
        :type indent_step: int

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
        :type src: typing.Any
        :param indent: start indentation
        :type indent: int
        :param no_indent_start:
            do not indent open bracket and simple parameters
        :type no_indent_start: bool
        :return: formatted string
        :rtype: typing.Text

    .. py:method:: __call__(src, indent=0, no_indent_start=False)

        Make human readable representation of object. The main entry point.

        :param src: object to process
        :type src: typing.Any
        :param indent: start indentation
        :type indent: int
        :param no_indent_start:
            do not indent open bracket and simple parameters
        :type no_indent_start: bool
        :return: formatted string
        :rtype: str


.. py:class:: PrettyRepr(PrettyFormat)

    Designed for usage as __repr__ replacement on complex objects

    .. versionadded:: 3.0.0
    .. versionchanged:: 3.0.1

    .. py:method:: __init__(max_indent=20, indent_step=4, )

        :param max_indent: maximal indent before classic repr() call
        :type max_indent: int
        :param indent_step: step for the next indentation level
        :type indent_step: int


.. py:class:: PrettyStr(PrettyFormat)

    Designed for usage as __repr__ replacement on complex objects

    .. versionadded:: 3.0.0
    .. versionchanged:: 3.0.1

    .. py:method:: __init__(max_indent=20, indent_step=4, )

        :param max_indent: maximal indent before classic repr() call
        :type max_indent: int
        :param indent_step: step for the next indentation level
        :type indent_step: int
