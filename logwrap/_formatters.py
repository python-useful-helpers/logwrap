#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""formatters module.

This is no reason to import this submodule directly, it's strictly internal
"""

from __future__ import absolute_import
from __future__ import unicode_literals

import six


def _strings_repr(indent, val):
    """Custom repr for strings and binary strings."""
    if isinstance(val, six.binary_type):
        val = val.decode(
            encoding='utf-8',
            errors='backslashreplace'
        )
        prefix = 'b'
    else:
        prefix = 'u'
    return "{spc:<{indent}}{prefix}'''{string}'''".format(
        spc='',
        indent=indent,
        prefix=prefix,
        string=val
    )


def _set_repr(indent, val):
    """Custom repr formatter for sets."""
    return "{spc:<{indent}}{val}".format(
        spc='',
        indent=indent,
        val="set({})".format(
            ' ,'.join(
                map(
                    '{!r}'.format,  # unicode -> !repr
                    val
                )
            )
        )
    )


s_repr_formatters = {
    'default': "{spc:<{indent}}{val!r}".format,
    set: _set_repr,
    six.binary_type: _strings_repr,
    six.text_type: _strings_repr,
}


c_repr_formatters = {
    'dict': "\n{spc:<{indent}}{key!r:{size}}: {val},".format,
    'iterable_item':
        "{nl}"
        "{spc:<{indent}}{obj_type:}({start}{result}\n"
        "{spc:<{indent}}{end})".format,
    'callable': "\n{spc:<{indent}}<{obj!r} with interface ({args})>".format,
    'func_arg': "\n{spc:<{indent}}{key},".format,
    'func_def_arg': "\n{spc:<{indent}}{key}={val},".format,
}


def _strings_str(indent, val):
    """Custom repr for strings and binary strings."""
    if isinstance(val, six.binary_type):
        val = val.decode(
            encoding='utf-8',
            errors='backslashreplace'
        )
    return "{spc:<{indent}}{string}".format(
        spc='',
        indent=indent,
        string=val
    )


def _set_str(indent, val):
    """Custom repr formatter for sets."""
    return "{spc:<{indent}}{val}".format(
        spc='',
        indent=indent,
        val="set({})".format(
            ' ,'.join(
                map(
                    '{!s}'.format,
                    val
                )
            )
        )
    )


s_str_formatters = {
    'default': "{spc:<{indent}}{val!s}".format,
    set: _set_str,
    six.binary_type: _strings_str,
    six.text_type: _strings_str,
}


c_str_formatters = {
    'dict': "\n{spc:<{indent}}{key!s:{size}}: {val},".format,
    'iterable_item':
        "{nl}"
        "{spc:<{indent}}{start}{result}\n"
        "{spc:<{indent}}{end}".format,
    'callable': "\n{spc:<{indent}}<{obj!s} with interface ({args})>".format,
    'func_arg': "\n{spc:<{indent}}{key},".format,
    'func_def_arg': "\n{spc:<{indent}}{key}={val},".format,
}


__all__ = (
    'c_repr_formatters', 's_repr_formatters',
    'c_str_formatters', 's_str_formatters',
)
