#    Copyright 2026 Aleksei Stepanov aka penguinolog
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at

#         http://www.apache.org/licenses/LICENSE-2.0

#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Traceback rendering helpers, which hide logwrap internals from the produced text."""

from __future__ import annotations

import os
import traceback
import typing

if typing.TYPE_CHECKING:
    from collections.abc import Container
    from collections.abc import Iterable

__all__ = ("format_traceback",)

_CURRENT_FILE = os.path.abspath(__file__)


def drop_frames_for_files(
    *,
    frames: Iterable[traceback.FrameSummary],
    filenames: Container[str],
) -> list[traceback.FrameSummary]:
    """Filter out frames, which belong to the decorator internals.

    :param frames: source frames
    :param filenames: absolute paths of files to hide
    :return: frames of the user code only
    """
    return [frame for frame in frames if frame.filename not in filenames]


def format_traceback(
    exception: BaseException,
    *,
    exclude_files: Iterable[str] = (),
) -> str:
    """Build a standard traceback text for the exception without the decorator internals.

    :param exception: exception to describe
    :param exclude_files: absolute paths of the decorator source files to hide from the traceback
    :return: traceback text, ready to be attached to a log record

    Frames above the decorator are taken from the live stack (the code, which did the call),
    frames below the decorator are taken from the exception traceback (the code, which failed),
    so the result looks like a normal traceback with the decorator frames cut out.

    .. versionadded:: 11.2.0
    """
    exclude: frozenset[str] = frozenset((*exclude_files, _CURRENT_FILE))
    # Callers of the decorated code: current stack up to the decorator internals.
    outer: list[traceback.FrameSummary] = drop_frames_for_files(
        frames=traceback.extract_stack(),
        filenames=exclude,
    )
    # Failed code itself: the exception traceback starts inside the decorator.
    inner: list[traceback.FrameSummary] = drop_frames_for_files(
        frames=traceback.extract_tb(exception.__traceback__),
        filenames=exclude,
    )
    exc_line: list[str] = traceback.format_exception_only(type(exception), exception)
    return f"Traceback (most recent call last):\n{''.join(traceback.format_list(outer + inner))}{''.join(exc_line)}"
