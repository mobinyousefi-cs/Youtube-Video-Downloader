# YouTube Video Downloader (Tkinter + pytube)

A clean, Pythonic GUI app to download YouTube videos using **pytube**.  
Built with a professional `src/` layout, tests, and CI.

> ⚠️ **Disclaimer**: Downloading YouTube content may violate YouTube’s Terms of Service and/or local laws, especially for copyrighted material or DRM-protected content. Use this tool only for content you own or have permission to download. You assume all responsibility.

## Features
- Paste a YouTube URL, fetch available streams
- Choose resolution/bitrate (video or audio)
- Pick output folder
- Responsive UI with progress bar
- Robust error handling

## Quick Start

```bash
# 1) Create & activate a venv
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 2) Install
pip install -r requirements.txt

# 3) Run (any of the following)
python -m youtube_downloader
# or
python src/youtube_downloader/main.py
