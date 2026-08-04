#!/usr/bin/env python3
"""Shared parser for uniquely marked, whole-line managed text blocks."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TypeVar


TextData = TypeVar("TextData", str, bytes)


class ManagedBlockError(ValueError):
    """Raised when a managed marker state is unsafe to edit or validate."""


@dataclass(frozen=True)
class BlockSpan:
    """Span for a managed block, including its final line ending when present."""

    start: int
    end: int


def _is_standalone_marker(data: TextData, position: int, marker: TextData) -> bool:
    newline = b"\n" if isinstance(data, bytes) else "\n"
    carriage_return = b"\r" if isinstance(data, bytes) else "\r"
    marker_end = position + len(marker)

    starts_line = position == 0 or data[position - 1 : position] == newline
    if marker_end == len(data):
        ends_line = True
    elif data[marker_end : marker_end + 1] == newline:
        ends_line = True
    else:
        ends_line = (
            data[marker_end : marker_end + 1] == carriage_return
            and data[marker_end + 1 : marker_end + 2] == newline
        )
    return starts_line and ends_line


def _next_fence_state(
    active_fence: tuple[str, int] | None, line: str
) -> tuple[str, int] | None:
    indentation = len(line) - len(line.lstrip(" "))
    if indentation > 3:
        return active_fence
    candidate = line[indentation:]

    if active_fence is not None:
        fence_character, opening_length = active_fence
        run_length = len(candidate) - len(candidate.lstrip(fence_character))
        remainder = candidate[run_length:]
        if run_length >= opening_length and not remainder.strip(" \t"):
            return None
        return active_fence

    if not candidate or candidate[0] not in {"`", "~"}:
        return None
    fence_character = candidate[0]
    run_length = len(candidate) - len(candidate.lstrip(fence_character))
    if run_length < 3:
        return None
    remainder = candidate[run_length:]
    if fence_character == "`" and "`" in remainder:
        return None
    return fence_character, run_length


def _is_inside_markdown_fence(data: TextData, position: int) -> bool:
    prefix = data[:position]
    if isinstance(prefix, bytes):
        text = prefix.decode("utf-8", errors="replace")
    else:
        text = prefix

    active_fence: tuple[str, int] | None = None
    for line in text.splitlines():
        active_fence = _next_fence_state(active_fence, line)
    return active_fence is not None


def markdown_h1_lines(text: str) -> list[str]:
    """Return ATX H1 lines outside fences, honoring CommonMark indentation."""

    headings: list[str] = []
    active_fence: tuple[str, int] | None = None
    for line in text.splitlines():
        was_inside_fence = active_fence is not None
        active_fence = _next_fence_state(active_fence, line)
        if was_inside_fence or active_fence is not None:
            continue

        indentation = len(line) - len(line.lstrip(" "))
        if indentation > 3:
            continue
        candidate = line[indentation:].rstrip(" \t")
        if re.match(r"^#(?:[ \t]+|$)", candidate):
            headings.append(candidate)
    return headings


def locate_managed_block(
    data: TextData,
    start_marker: TextData,
    end_marker: TextData,
    label: str,
) -> BlockSpan | None:
    """Locate one ordered whole-line block, or reject any malformed marker state."""

    start_count = data.count(start_marker)
    end_count = data.count(end_marker)
    if start_count == 0 and end_count == 0:
        return None
    if start_count != 1 or end_count != 1:
        raise ManagedBlockError(
            f"{label} marker 必须各出现一次，且不得缺失或重复"
        )

    start = data.index(start_marker)
    end_start = data.index(end_marker)
    if not _is_standalone_marker(data, start, start_marker) or not _is_standalone_marker(
        data, end_start, end_marker
    ):
        raise ManagedBlockError(f"{label} marker 必须独占整行")
    if _is_inside_markdown_fence(data, start) or _is_inside_markdown_fence(
        data, end_start
    ):
        raise ManagedBlockError(f"{label} marker 不得位于 Markdown 代码围栏内")
    if end_start < start:
        raise ManagedBlockError(f"{label} marker 顺序错误")

    end = end_start + len(end_marker)
    crlf = b"\r\n" if isinstance(data, bytes) else "\r\n"
    newline = b"\n" if isinstance(data, bytes) else "\n"
    if data[end : end + 2] == crlf:
        end += 2
    elif data[end : end + 1] == newline:
        end += 1
    return BlockSpan(start=start, end=end)
