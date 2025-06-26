# ===========================================
# Author: Zeldean
# Project: Movie Manager V2.10 (Dry‑Run by default)
# Date: June 26, 2025
# ===========================================
#   ______      _      _                     
#  |___  /     | |    | |                    
#     / /  ___ | |  __| |  ___   __ _  _ __  
#    / /  / _ \| | / _` | / _ \ / _` || '_ \ 
#   / /__|  __/| || (_| ||  __/| (_| || | | |
#  /_____|\___||_| \__,_| \___| \__,_||_| |_|
# ===========================================

"""Movie Manager V2.10 – *dry‑run mode*

Patch release – **Fix parentheses‑year bug**
-------------------------------------------
* `Dawn_of_the_Planet_of_the_Apes(2014).mp4` now →
  `Dawn_of_the_Planet_of_the_Apes_(2014).mp4` (previously “20”).
* Implemented with a named‑group regex so we capture **all four digits**.
* All prior features (smart sequel numbers, tag stripping, skip already
  formatted, etc.) remain unchanged.

Flip ``DRY_RUN`` to ``False`` after verifying the dry‑run output.
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

DRY_RUN = True  # ⇦ switch to False to actually move/rename files

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
# Capture full 4‑digit year inside parentheses via named group "year"
PAREN_YEAR_SEARCH = re.compile(r"\((?P<year>(?:19|20)\d{2})\)")
READY_PATTERN = re.compile(r"_\((19|20)\d{2}\)$")  # filename already ok

_UNWANTED_EQUAL = {w.lower() for w in UNWANTED_WORDS}

# --------------------------------------------------------------------------- #
# Core helpers                                                                #
# --------------------------------------------------------------------------- #

def find_video_files(folder: Path) -> list[Path]:
    return [p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in VIDEO_EXTS]


def is_unwanted(token: str) -> bool:
    return token.lower() in _UNWANTED_EQUAL


def build_clean_name(original: Path) -> Path:
    stem = original.stem

    # 0. Already correct? Bail early
    if READY_PATTERN.search(stem):
        return original

    # 1. Pull out an embedded (YEAR)
    year: str | None = None
    m = PAREN_YEAR_SEARCH.search(stem)
    if m:
        year = m.group("year")  # full 4‑digit year
        stem = stem[: m.start()] + stem[m.end():]  # strip the "(YEAR)" from stem

    # 2. Tokenise
    tokens = re.split(r"[.\-_ ]+", stem)

    title_parts: List[str] = []
    for token in tokens:
        if not token:
            continue
        # Year detection (if still missing)
        if year is None and YEAR_RE.fullmatch(token):
            year = token
            continue
        # Unwanted exact tag
        if is_unwanted(token):
            continue
        # Skip bracketed junk entirely
        if any(ch in token for ch in "[]{}()"):
            continue
        # Numeric sequel logic – keep short number only if before year is seen
        if token.isdigit() and len(token) < 4:
            if year is None:
                title_parts.append(token)
            continue
        # Otherwise keep token
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
