# ===========================================
# Author: Zeldean
# Project: Movie Manager V2.5 (Dry‑Run by default)
# Date: June 26, 2025
# ===========================================
#   ______      _      _                     
#  |___  /     | |    | |                    
#     / /  ___ | |  __| |  ___   __ _  _ __  
#    / /  / _ \| | / _` | / _ \ / _` || '_ \ 
#   / /__|  __/| || (_| ||  __/| (_| || | | |
#  /_____|\___||_| \__,_| \___| \__,_||_| |_|
# ===========================================

"""Movie Manager V2.5 – *dry‑run mode*

This version is **non‑destructive by default**: all file moves/renames are
*printed* instead of executed so you can verify the results. To perform the
actual operations simply set ``DRY_RUN = False`` below.

Steps performed:
 1. Recursively locate video files in the *source* directory.
 2. Print the move that *would* copy them into the destination, prefixing
    duplicates with "[DUP] ".
 3. Print how destination filenames *would* be cleaned to
        ``Title_Words_(YEAR).ext``.

Running the script twice with ``DRY_RUN = True`` causes **no changes** on
 disk.
"""

from __future__ import annotations

import logging
import os
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

DRY_RUN = True  # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# Flip to False after verifying the printed output.

# Tag & pattern definitions -------------------------------------------------- #

UNWANTED_WORDS: set[str] = {
    "1080p", "720p", "2160p", "4k", "4K",
    "BluRay", "WEBRip", "BRrip", "BRRip", "WEB", "HDRip", "DVDRip",
    "x264", "x265", "H264", "H265", "HEVC",
    "AAC", "AAC5", "DDP5", "DDP5_1", "DTS", "Atmos",
    "YIFY", "YTS", "AM", "MX", "REPACK", "PROPER",
    "sample", "trailer",
}

VIDEO_EXTS: tuple[str, ...] = (".mp4", ".mkv", ".avi")
YEAR_RE = re.compile(r"^(19|20)\d{2}$")

# --------------------------------------------------------------------------- #
# Core helpers                                                                #
# --------------------------------------------------------------------------- #

def find_video_files(folder: Path) -> list[Path]:
    """Return a list of all *video* files inside *folder* (recursive)."""
    return [
        p
        for p in folder.rglob("*")
        if p.is_file() and p.suffix.lower() in VIDEO_EXTS
    ]


def is_unwanted(token: str) -> bool:
    return token.lower() in {w.lower() for w in UNWANTED_WORDS}


def build_clean_name(original: Path) -> Path:
    """Return a new Path with a cleaned filename according to the spec."""
    tokens = original.stem.split(".")
    title_parts: List[str] = []
    year: str | None = None

    for token in tokens:
        if YEAR_RE.fullmatch(token):
            year = token
            continue
        if is_unwanted(token):
            continue
        title_parts.append(token)

    if not title_parts:
        logging.warning("Could not derive title from %s – leaving as-is", original.name)
        return original

    title = "_".join(title_parts)
    new_stem = f"{title}_({year})" if year else title
    return original.with_name(f"{new_stem}{original.suffix}")


# --------------------------------------------------------------------------- #
# File operations (dry‑run aware)                                             #
# --------------------------------------------------------------------------- #

def move_files_to_folder(files: Iterable[Path], destination: Path) -> None:
    """Move or *pretend* to move *files* into *destination*."""
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
    """Rename—or just print—the cleaned names inside *folder*."""
    logging.info("Cleaning movie names…")
    movie_files = list(folder.iterdir())

    for file_path in tqdm(movie_files, desc="Renaming", unit="file"):
        if file_path.suffix.lower() not in VIDEO_EXTS:
            continue
        new_path = build_clean_name(file_path)
        if new_path.name == file_path.name:
            continue  # no change

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

if __name__ == "__main__":  # pragma: no cover
    src = prompt_path("Enter the source folder path: ")
    dst = prompt_path("Enter the destination folder path: ")
    save_paths({
        "Enter the source folder path: ": str(src),
        "Enter the destination folder path: ": str(dst),
    })

    move_files_to_folder(find_video_files(src), dst)
    clean_movie_names(dst)
    logging.info("Dryrun complete! Review the actions above. Set DRY_RUN = False when ready.")
