"""
Shared constants & regex patterns.
"""
from pathlib import Path
import re

# Video extensions we treat as “movies”
VIDEO_EXTS: tuple[str, ...] = (".mp4", ".mkv", ".avi")

# Regex for filenames like ‘Some_Movie_(2024).mp4’
MOVIE_RE = re.compile(
    r"""^(?P<title>.+?)_\((?P<year>\d{4})\)\.[^.]+$""",
    re.VERBOSE,
)

# Words we strip when cleaning scene releases
UNWANTED_WORDS: set[str] = {
    "1080p", "720p", "2160p", "4k", "uhd",
    "bluray", "webrip", "brrip", "hdrip", "dvdrip",
    "x264", "x265", "h264", "h265", "hevc",
    "aac", "aac5", "ddp5", "ddp5_1", "dts", "atmos",
    "yify", "yts", "repack", "proper", "sample", "trailer", "BOKUTOX",
}
_UNWANTED_EQUAL = {w.lower() for w in UNWANTED_WORDS}

# Extra regexes used by rename.py
YEAR_RE = re.compile(r"^(19|20)\d{2}$")
PAREN_YEAR_SEARCH = re.compile(r"\((?P<year>(?:19|20)\d{2})\)")
READY_PATTERN = re.compile(r"_\((19|20)\d{2}\)$")

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)
PATHS_JSON = DATA_DIR / "paths.json"
PATHS_JSON.touch(exist_ok=True)
