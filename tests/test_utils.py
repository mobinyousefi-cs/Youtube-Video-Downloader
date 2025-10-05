#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic tests for utility helpers.
"""

from youtube_downloader.utils import is_probable_youtube_url, sanitize_filename


def test_is_probable_youtube_url_accepts_common_forms():
    assert is_probable_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert is_probable_youtube_url("http://youtube.com/watch?v=abcdefg")
    assert is_probable_youtube_url("https://youtu.be/abcdefg12345")


def test_is_probable_youtube_url_rejects_invalid():
    assert not is_probable_youtube_url("https://example.com/watch?v=dQw4w9WgXcQ")
    assert not is_probable_youtube_url("not-a-url")


def test_sanitize_filename_basic():
    assert sanitize_filename("My*Great:Video?") == "My_Great_Video"
    assert sanitize_filename("   ") == "video"
