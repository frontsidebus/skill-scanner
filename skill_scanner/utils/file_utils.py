# Copyright 2026 Cisco Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

"""
File utility functions.
"""

import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class TextReadResult:
    """Result of attempting to read a file as validated UTF-8 text."""

    content: str | None
    is_binary: bool
    reason: str | None = None


def read_utf8_validated(file_path: Path, *, max_size_bytes: int = 0) -> TextReadResult:
    """Read a file as UTF-8 text with null-byte and encoding validation.

    Args:
        file_path: Path to file.
        max_size_bytes: Skip reading if file exceeds this size.
            0 means no limit.

    Returns:
        TextReadResult with content (if valid UTF-8 text) or binary flag.
    """
    try:
        raw = file_path.read_bytes()
    except OSError as e:
        return TextReadResult(content=None, is_binary=True, reason=f"unreadable: {e}")

    if max_size_bytes and len(raw) > max_size_bytes:
        return TextReadResult(content=None, is_binary=False, reason="exceeds size limit")

    if b"\x00" in raw:
        return TextReadResult(content=None, is_binary=True, reason="contains null bytes")

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        return TextReadResult(content=None, is_binary=True, reason=f"not valid UTF-8: {e}")

    return TextReadResult(content=text, is_binary=False)


def read_file_safe(file_path: Path, max_size_mb: int = 10) -> str | None:
    """
    Safely read a file with size limit.

    Args:
        file_path: Path to file
        max_size_mb: Maximum file size in MB

    Returns:
        File content or None if unreadable/binary
    """
    result = read_utf8_validated(file_path, max_size_bytes=max_size_mb * 1024 * 1024)
    return result.content


def get_file_type(file_path: Path) -> str:
    """
    Determine file type from extension.

    Args:
        file_path: Path to file

    Returns:
        File type string
    """
    suffix = file_path.suffix.lower()

    type_mapping = {
        ".py": "python",
        ".sh": "bash",
        ".bash": "bash",
        ".js": "javascript",
        ".mjs": "javascript",
        ".cjs": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".md": "markdown",
        ".markdown": "markdown",
        ".exe": "binary",
        ".so": "binary",
        ".dylib": "binary",
        ".dll": "binary",
        ".bin": "binary",
    }

    return type_mapping.get(suffix, "other")


def is_binary_file(file_path: Path) -> bool:
    """
    Check if file is binary.

    Args:
        file_path: Path to file

    Returns:
        True if binary
    """
    return get_file_type(file_path) == "binary"
