#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=========================================================================================================
Project: YouTube Video Downloader
File: downloader.py
Author: Mobin Yousefi (GitHub: https://github.com/mobinyousefi-cs)
Created: 2025-10-05
Updated: 2025-10-05
License: MIT License (see LICENSE file for details)
=========================================================================================================

Description:
Core download logic using pytube with progress callbacks and robust error handling.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional

from pytube import YouTube
from pytube.exceptions import PytubeError

from .utils import sanitize_filename


@dataclass(frozen=True)
class StreamInfo:
    itag: int
    type: str                # "video" | "audio"
    mime_type: str
    resolution_or_abr: str   # e.g., "1080p" or "160kbps"
    progressive: bool
    filesize: Optional[int]
    pretty: str              # Human-readable label


class YouTubeDownloader:
    """Encapsulates loading streams and downloading with progress reporting."""

    def __init__(self, url: str, on_progress: Optional[Callable[[int, int], None]] = None):
        """
        Args:
            url: YouTube video URL.
            on_progress: optional callback (bytes_received, total_bytes).
        """
        self.url = url.strip()
        self.on_progress = on_progress
        self._yt: Optional[YouTube] = None

    def _pytube_progress(self, stream, chunk: bytes, bytes_remaining: int):
        total = stream.filesize or 0
        received = max(total - bytes_remaining, 0)
        if self.on_progress:
            self.on_progress(received, total)

    def _pytube_complete(self, stream, file_path: str):
        # No-op hook; GUI handles completion message
        pass

    def load(self) -> None:
        """Initialize the YouTube object."""
        try:
            self._yt = YouTube(
                self.url,
                on_progress_callback=self._pytube_progress,
                on_complete_callback=self._pytube_complete,
                use_oauth=False,
                allow_oauth_cache=True,
            )
        except Exception as ex:  # keep broad for pytube’s varying exceptions
            raise RuntimeError(f"Failed to initialize YouTube object: {ex}") from ex

    @property
    def title(self) -> str:
        if not self._yt:
            raise RuntimeError("YouTube object not loaded. Call load() first.")
        return self._yt.title

    def available_streams(self) -> List[StreamInfo]:
        """Return available streams (video progressive/adaptive + audio)."""
        if not self._yt:
            raise RuntimeError("YouTube object not loaded. Call load() first.")

        infos: List[StreamInfo] = []

        # Video (progressive contains both audio+video)
        for s in self._yt.streams.filter(type="video").order_by("resolution").desc():
            res = getattr(s, "resolution", None) or "N/A"
            progressive = bool(getattr(s, "is_progressive", False))
            infos.append(
                StreamInfo(
                    itag=s.itag,
                    type="video",
                    mime_type=s.mime_type or "video/mp4",
                    resolution_or_abr=res,
                    progressive=progressive,
                    filesize=getattr(s, "filesize", None),
                    pretty=f"VIDEO | {res} | {'progressive' if progressive else 'adaptive'} | {s.mime_type}",
                )
            )

        # Audio only
        for s in self._yt.streams.filter(only_audio=True).order_by("abr").desc():
            abr = getattr(s, "abr", None) or "N/A"
            infos.append(
                StreamInfo(
                    itag=s.itag,
                    type="audio",
                    mime_type=s.mime_type or "audio/mp4",
                    resolution_or_abr=abr,
                    progressive=False,
                    filesize=getattr(s, "filesize", None),
                    pretty=f"AUDIO | {abr} | {s.mime_type}",
                )
            )

        return infos

    def download(self, itag: int, output_dir: str) -> str:
        """Download a selected stream by itag to the output directory.

        Returns:
            Path to the downloaded file.
        """
        if not self._yt:
            raise RuntimeError("YouTube object not loaded. Call load() first.")

        stream = self._yt.streams.get_by_itag(itag)
        if stream is None:
            raise ValueError(f"No stream found for itag={itag}")

        safe_title = sanitize_filename(self._yt.title)
        try:
            # pytube handles filename; we provide a safe base
            filepath = stream.download(output_path=output_dir, filename_prefix="")
        except PytubeError as ex:
            raise RuntimeError(f"pytube error: {ex}") from ex
        except Exception as ex:
            raise RuntimeError(f"Unexpected download error: {ex}") from ex

        return filepath
