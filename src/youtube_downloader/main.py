#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=========================================================================================================
Project: YouTube Video Downloader
File: main.py
Author: Mobin Yousefi (GitHub: https://github.com/mobinyousefi-cs)
Created: 2025-10-05
Updated: 2025-10-05
License: MIT License (see LICENSE file for details)
=========================================================================================================

Description:
Tkinter GUI application for downloading YouTube videos using pytube.
Features:
- URL validation
- Fetch & select stream (resolution/bitrate)
- Choose output folder
- Progress bar with percentage
- Threaded downloads to keep UI responsive
"""

from __future__ import annotations

import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Optional

from .downloader import YouTubeDownloader, StreamInfo
from .utils import ensure_directory, is_probable_youtube_url
from . import __version__


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"YouTube Video Downloader v{__version__}")
        self.geometry("720x420")
        self.minsize(660, 380)

        self._downloader: Optional[YouTubeDownloader] = None
        self._streams: list[StreamInfo] = []
        self._selected_itag: Optional[int] = None
        self._total_bytes: int = 0

        self._build_ui()

    # ---------------------- UI ----------------------
    def _build_ui(self):
        pad = {"padx": 10, "pady": 6}

        frm = ttk.Frame(self)
        frm.pack(fill=tk.BOTH, expand=True)

        # URL input
        ttk.Label(frm, text="YouTube URL:").grid(row=0, column=0, sticky="w", **pad)
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(frm, textvariable=self.url_var, width=60)
        self.url_entry.grid(row=0, column=1, columnspan=2, sticky="we", **pad)

        self.fetch_btn = ttk.Button(frm, text="Fetch Streams", command=self.on_fetch_streams)
        self.fetch_btn.grid(row=0, column=3, sticky="e", **pad)

        # Streams list
        ttk.Label(frm, text="Available Streams:").grid(row=1, column=0, sticky="w", **pad)
        self.streams_cmb = ttk.Combobox(frm, state="readonly", width=60)
        self.streams_cmb.grid(row=1, column=1, columnspan=2, sticky="we", **pad)
        self.streams_cmb.bind("<<ComboboxSelected>>", self.on_select_stream)

        # Folder selection
        ttk.Label(frm, text="Output Folder:").grid(row=2, column=0, sticky="w", **pad)
        self.out_var = tk.StringVar(value=str(ensure_directory("./downloads")))
        self.out_entry = ttk.Entry(frm, textvariable=self.out_var, width=60)
        self.out_entry.grid(row=2, column=1, sticky="we", **pad)
        self.browse_btn = ttk.Button(frm, text="Choose…", command=self.on_browse)
        self.browse_btn.grid(row=2, column=2, sticky="w", **pad)

        # Progress
        ttk.Label(frm, text="Progress:").grid(row=3, column=0, sticky="w", **pad)
        self.progress = ttk.Progressbar(frm, orient="horizontal", length=100, mode="determinate")
        self.progress.grid(row=3, column=1, columnspan=2, sticky="we", **pad)
        self.progress_label = ttk.Label(frm, text="0%")
        self.progress_label.grid(row=3, column=3, sticky="e", **pad)

        # Action buttons
        self.download_btn = ttk.Button(frm, text="Download", command=self.on_download, state=tk.DISABLED)
        self.download_btn.grid(row=4, column=1, sticky="e", **pad)

        self.quit_btn = ttk.Button(frm, text="Quit", command=self.destroy)
        self.quit_btn.grid(row=4, column=2, sticky="w", **pad)

        # Status
        self.status = ttk.Label(frm, text="Ready.", relief=tk.SUNKEN, anchor="w")
        self.status.grid(row=5, column=0, columnspan=4, sticky="we", padx=6, pady=(12, 6))

        # grid config
        frm.columnconfigure(1, weight=1)
        frm.columnconfigure(2, weight=1)

    # ------------------ Event handlers ------------------
    def on_browse(self):
        folder = filedialog.askdirectory(initialdir=self.out_var.get() or ".")
        if folder:
            self.out_var.set(folder)

    def on_fetch_streams(self):
        url = self.url_var.get().strip()
        if not is_probable_youtube_url(url):
            messagebox.showerror("Invalid URL", "Please paste a valid YouTube video URL.")
            return

        self.set_busy(True, "Loading video info…")
        self.progress["value"] = 0
        self.progress_label.config(text="0%")
        self.download_btn.config(state=tk.DISABLED)
        self.streams_cmb.set("")
        self.streams_cmb["values"] = []

        def task():
            try:
                self._downloader = YouTubeDownloader(url, on_progress=self.on_progress)
                self._downloader.load()
                self._streams = self._downloader.available_streams()
                options = [s.pretty for s in self._streams]
                self.after(0, lambda: self._populate_streams(options))
            except Exception as ex:
                self.after(0, lambda: messagebox.showerror("Fetch Error", str(ex)))
            finally:
                self.after(0, lambda: self.set_busy(False, "Ready."))

        threading.Thread(target=task, daemon=True).start()

    def _populate_streams(self, options: list[str]):
        if not options:
            self.status.config(text="No streams found.")
            return
        self.streams_cmb["values"] = options
        self.streams_cmb.current(0)
        self.on_select_stream()

    def on_select_stream(self, _evt=None):
        idx = self.streams_cmb.current()
        if 0 <= idx < len(self._streams):
            self._selected_itag = self._streams[idx].itag
            self.download_btn.config(state=tk.NORMAL)
        else:
            self._selected_itag = None
            self.download_btn.config(state=tk.DISABLED)

    def on_download(self):
        if not self._downloader or self._selected_itag is None:
            messagebox.showerror("Selection Required", "Please fetch streams and select one.")
            return

        out_dir = self.out_var.get().strip()
        if not out_dir:
            messagebox.showerror("Output Folder", "Please choose an output folder.")
            return

        self.set_busy(True, "Downloading…")
        self.progress["value"] = 0
        self.progress_label.config(text="0%")

        def task():
            try:
                path = self._downloader.download(self._selected_itag, out_dir)
                self.after(0, lambda: messagebox.showinfo("Completed", f"Downloaded:\n{path}"))
            except Exception as ex:
                self.after(0, lambda: messagebox.showerror("Download Error", str(ex)))
            finally:
                self.after(0, lambda: self.set_busy(False, "Ready."))

        threading.Thread(target=task, daemon=True).start()

    def on_progress(self, bytes_received: int, total_bytes: int):
        self._total_bytes = total_bytes
        percent = 0 if total_bytes <= 0 else int((bytes_received / total_bytes) * 100)
        self.progress["value"] = percent
        self.progress_label.config(text=f"{percent}%")

    def set_busy(self, busy: bool, status: str):
        widgets = [self.fetch_btn, self.browse_btn, self.download_btn, self.url_entry, self.streams_cmb, self.out_entry]
        for w in widgets:
            try:
                w.config(state=tk.DISABLED if busy else tk.NORMAL)
            except tk.TclError:
                pass
        self.status.config(text=status)


def run_app():
    app = App()
    app.mainloop()
