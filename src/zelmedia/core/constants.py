"""
Shared constants & regex patterns for ZelMedia.
Runtime files go to  ~/.local/state/zel/zelmedia/paths.json
(or  %XDG_STATE_HOME%/zel/zelmedia/paths.json  when the env-var is set).
"""
from pathlib import Path
import os
import re

# ───────────────────────── video file types ──────────────────────────
VIDEO_EXTS: tuple[str, ...] = (".mp4", ".mkv", ".avi")

# ───────────────────────── filename patterns ─────────────────────────
MOVIE_RE = re.compile(r"""^(?P<title>.+?)_\((?P<year>\d{4})\)\.[^.]+$""", re.VERBOSE)

UNWANTED_WORDS: set[str] = {
    "1080p", "720p", "2160p", "4k", "uhd",
    "bluray", "webrip", "brrip", "hdrip", "dvdrip",
    "x264", "x265", "h264", "h265", "hevc",
    "aac", "aac5", "ddp5", "ddp5_1", "dts", "atmos",
    "yify", "yts", "repack", "proper",
    "sample", "trailer", "BOKUTOX",
}
_UNWANTED_EQUAL = {w.lower() for w in UNWANTED_WORDS}

YEAR_RE           = re.compile(r"^(19|20)\d{2}$")
PAREN_YEAR_SEARCH = re.compile(r"\((?P<year>(?:19|20)\d{2})\)")
READY_PATTERN     = re.compile(r"_\((19|20)\d{2}\)$")

# ─────────────────────── runtime data location ───────────────────────
# ~/.local/state/zel/zelmedia/   (or $XDG_STATE_HOME)
_DATA_ROOT = Path(os.getenv("XDG_STATE_HOME", "~/.local/state")).expanduser() / "zel" / "zelmedia"
_DATA_ROOT.mkdir(parents=True, exist_ok=True)

PATHS_JSON = _DATA_ROOT / "paths.json"   # file is created on first save()
