"""
Functions for discovering movie files and parsing basic fields.
"""
from pathlib import Path
from typing import List, Dict

from .constants import MOVIE_RE, VIDEO_EXTS


def list_movies(root: str | Path = ".") -> List[Dict]:
    """
    Walk *root* and return `[{"title": str, "year": int, "file": str}, …]`
    for every valid movie filename.
    """
    root = Path(root)
    movies = []
    patterns = [root.glob(f"*{ext}") for ext in VIDEO_EXTS]
    for path_iter in patterns:
        for file in path_iter:
            m = MOVIE_RE.match(file.name)
            if not m:
                continue
            title = m.group("title").replace("_", " ")
            movies.append(
                {"title": title,
                 "year": int(m.group("year")),
                 "file": str(file.resolve())}
            )
    return movies


def find_video_files(folder: Path) -> list[Path]:
    """Return **all** video files inside *folder* recursively."""
    return [p for p in folder.rglob("*") if p.suffix.lower() in VIDEO_EXTS]
