# ===========================================
# Author: Zeldean
# Project: Movie Manager V2.7 (Dry‑Run by default)
# Date: June 26, 2025
# ===========================================
#   ______      _      _                     
#  |___  /     | |    | |                    
#     / /  ___ | |  __| |  ___   __ _  _ __  
#    / /  / _ \| | / _` | / _ \ / _` || '_ \ 
#   / /__|  __/| || (_| ||  __/| (_| || | | |
#  /_____|\___||_| \__,_| \___| \__,_||_| |_|
# ===========================================

"""Movie Manager V2.7 – *dry‑run mode*

Changes vs. 2.6
---------------
1. **Keep files already in the right format** – if the stem ends with
   ``_(YEAR)`` we now *skip* any rename.
2. **Accurate tag filtering** – `is_unwanted()` is now *equality* based to
   avoid false positives like *"America"* matching the tag *"AM"*.
3. **Detect year inside parentheses** – tokens like ``(2019)`` are
   recognised and preserved.

As before, set ``DRY_RUN = False`` to perform the actual moves/renames.
"""

from __future__ import annotations

import logging
import pickle
import re
import shutil
from pathlib import Path
from typing import Iterable, List

from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# --------------------------------------------------------------------------- #
# Configuration                                                               #
# --------------------------------------------------------------------------- #

DRY_RUN = True  # ⇦ toggle when satisfied with dry‑run output

UNWANTED_WORDS: set[str] = {
    # Resolution / quality
    "1080p", "720p", "2160p", "4k", "uhd",
    # Source / codec
    "bluray", "webrip", "brrip", "hdrip", "dvdrip",
    "x264", "x265", "h264", "h265", "hevc",
    # Audio / misc
    "aac", "aac5", "ddp5", "ddp5_1", "dts", "atmos",
    # Scene groups / misc flags
    "yify", "yts", "repack", "proper",
    # Other noise
    "sample", "trailer",
}

VIDEO_EXTS: tuple[str, ...] = (".mp4", ".mkv", ".avi")
YEAR_RE = re.compile(r"^(19|20)\d{2}$")
PAREN_YEAR_RE = re.compile(r"^\((19|20)\d{2}\)$")
READY_PATTERN = re.compile(r"_\((19|20)\d{2}\)$")  # title already ok

# Lower‑cased set for equality check
_UNWANTED_EQUAL = {w.lower() for w in UNWANTED_WORDS}

# --------------------------------------------------------------------------- #
# Core helpers                                                                #
# --------------------------------------------------------------------------- #

def find_video_files(folder: Path) -> list[Path]:
    return [p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in VIDEO_EXTS]


def is_unwanted(token: str) -> bool:
    """Exact match test: token (lower‑cased) must *equal* an unwanted tag."""
    return token.lower() in _UNWANTED_EQUAL


def build_clean_name(original: Path) -> Path:
    """Return a new Path with a cleaned filename or *original* if already good."""
    stem = original.stem

    # 1. Short‑circuit: already `Title_(YEAR)`? —> leave untouched
    if READY_PATTERN.search(stem):
        return original

    # 2. Tokenise on dot/dash/underscore/space
    tokens = re.split(r"[.\-_ ]+", stem)
    title_parts: List[str] = []
    year: str | None = None

    for token in tokens:
        if not token:
            continue
        if YEAR_RE.fullmatch(token):
            year = token
            continue
        if PAREN_YEAR_RE.fullmatch(token):
            year = token.strip("()")  # capture without parentheses
            continue
        if is_unwanted(token):
            continue
        # Drop stray bracketed pieces like "[YTS"
        if any(ch in token for ch in "[]{}()"):
            continue
        title_parts.append(token)

    if not title_parts:
        logging.warning("Could not derive title from %s – leaving as‑is", original.name)
        return original

    title = "_".join(title_parts)
    new_stem = f"{title}_({year})" if year else title
    return original.with_name(new_stem + original.suffix)


# --------------------------------------------------------------------------- #
# File operations (dry‑run aware)                                             #
# --------------------------------------------------------------------------- #

def move_files_to_folder(files: Iterable[Path], destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for file_path in tqdm(files, desc="Moving files", unit="file"):
        target = destination / file_path.name
        if target.exists():
            dup_target = destination / f"[DUP] {file_path.name}"
            action = f"Would move {file_path} → {dup_target}"
            if DRY_RUN:
                print(action)
            else:
                shutil.move(file_path, dup_target)
        else:
            action = f"Would move {file_path} → {target}"
            if DRY_RUN:
                print(action)
            else:
                shutil.move(file_path, target)


def clean_movie_names(folder: Path) -> None:
    logging.info("Cleaning movie names…")
    for file_path in tqdm(list(folder.iterdir()), desc="Renaming", unit="file"):
        if file_path.suffix.lower() not in VIDEO_EXTS:
            continue
        new_path = build_clean_name(file_path)
        if new_path.name == file_path.name:
            continue
        action = f"Would rename {file_path.name} → {new_path.name}"
        if DRY_RUN:
            print(action)
        else:
            file_path.rename(new_path)


# --------------------------------------------------------------------------- #
# Persistence utilities                                                       #
# --------------------------------------------------------------------------- #

PATHS_PKL = Path("paths.pkl")


def load_saved_path(prompt: str) -> str | None:
    if not PATHS_PKL.exists():
        return None
    with PATHS_PKL.open("rb") as f:
        paths: dict[str, str] = pickle.load(f)
    return paths.get(prompt)


def save_paths(paths: dict[str, str]) -> None:
    with PATHS_PKL.open("wb") as f:
        pickle.dump(paths, f)


def prompt_path(message: str) -> Path:
    user_input = input(message).strip()
    if not user_input:
        user_input = load_saved_path(message) or input("Please enter a valid path: ").strip()
    path = Path(user_input).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist")
    return path


# --------------------------------------------------------------------------- #
# Main routine                                                                #
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    src = prompt_path("Enter the source folder path: ")
    dst = prompt_path("Enter the destination folder path: ")
    save_paths({
        "Enter the source folder path: ": str(src),
        "Enter the destination folder path: ": str(dst),
    })

    move_files_to_folder(find_video_files(src), dst)
    clean_movie_names(dst)
    logging.info("Dry‑run complete! Review the actions above. Set DRY_RUN = False when ready.")
