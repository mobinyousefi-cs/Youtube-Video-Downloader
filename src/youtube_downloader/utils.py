#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=========================================================================================================
Project: YouTube Video Downloader
File: utils.py
Author: Mobin Yousefi (GitHub: https://github.com/mobinyousefi-cs)
Created: 2025-10-05
Updated: 2025-10-05
License: MIT License (see LICENSE file for details)
=========================================================================================================

Description:
Utility helpers for validation, formatting, and safe filename creation.
"""

from __future__ import annotations

import re
import string
from pathlib import Path


_YT_URL_RE = re.compile(
    r"""^
    (?:https?://)?
    (?:www\.)?
    (?:youtube\.com/watch\?v=|youtu\.be/)
    [A-Za-z0-9_\-]{6,}   # video id
    """,
    re.VERBOSE,
)


def is_probable_youtube_url(url: str) -> bool:
    """Quick heuristic validation for YouTube watch/short URLs."""
    if not isinstance(url, str):
        return False
    url = url.strip()
    return bool(_YT_URL_RE.match(url))


def sanitize_filename(name: str, max_len: int = 180) -> str:
    """Make a filesystem-safe filename."""
    allowed = f"-_.() {string.ascii_letters}{string.digits}"
    cleaned = "".join(c if c in allowed else "_" for c in name).strip(" ._")
    if len(cleaned) > max_len:
        cleaned = cleaned[: max_len - 3] + "..."
    return cleaned or "video"


def ensure_directory(path: str | Path) -> Path:
    """Create directory if missing and return Path."""
    p = Path(path).expanduser().resolve()
    p.mkdir(parents=True, exist_ok=True)
    return p
