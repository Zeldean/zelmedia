# ===========================================
# Author: Zeldean
# Project: Movie Manager V2.4
# Date: June 26, 2025
# ===========================================
#   ______      _      _                     
#  |___  /     | |    | |                    
#     / /  ___ | |  __| |  ___   __ _  _ __  
#    / /  / _ \| | / _` | / _ \ / _` || '_ \ 
#   / /__|  __/| || (_| ||  __/| (_| || | | |
#  /_____|\___||_| \__,_| \___| \__,_||_| |_|
# ===========================================

"""Movie Manager V2.4

This script performs three operations:

1. Recursively finds video files in a *source* folder.
2. Moves them to the *destination* folder, adding a "[DUP]" prefix when
   a file of the same name already exists.
3. Cleans up all filenames in the destination folder so they follow the
   pattern::

      Movie_Name_(YEAR).ext

Unwanted rip‑tags such as *1080p*, *BluRay*, *x264*, etc. are stripped
during the clean‑up step.

Usage
-----
Run the script and follow the interactive prompts, or leave the prompts
blank to reuse the last‑entered paths (stored in ``paths.pkl``).

Dependencies
------------
* tqdm   – progress bars
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
# Tag & pattern definitions                                                   #
# --------------------------------------------------------------------------- #

UNWANTED_WORDS: set[str] = {
    # Resolutions / quality
    "1080p", "720p", "2160p", "4k", "4K",
    # Source or codec
    "BluRay", "WEBRip", "BRrip", "BRRip", "WEB", "HDRip", "DVDRip",
    "x264", "x265", "H264", "H265", "HEVC",
    # Audio
    "AAC", "AAC5", "DDP5", "DDP5_1", "DTS", "Atmos",
    # Scene tags / groups
    "YIFY", "YTS", "AM", "MX", "REPACK", "PROPER",
    # Other noise
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
    """Case‑insensitive membership test *token* ∈ UNWANTED_WORDS."""
    return token.lower() in {w.lower() for w in UNWANTED_WORDS}


def build_clean_name(original: Path) -> Path:
    """Return a *new* Path with a cleaned filename according to the spec."""
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
        # Fallback: keep original stem if nothing was salvageable
        logging.warning("Could not derive title from %s – leaving as‑is", original.name)
        return original

    title = "_".join(title_parts)

    new_stem = f"{title}_({year})" if year else title
    return original.with_name(f"{new_stem}{original.suffix}")


def move_files_to_folder(files: Iterable[Path], destination: Path) -> None:
    """Move *files* into *destination*, handling duplicates."""
    destination.mkdir(parents=True, exist_ok=True)
    for file_path in tqdm(files, desc="Moving files", unit="file"):
        target = destination / file_path.name
        if target.exists():
            dup_target = destination / f"[DUP] {file_path.name}"
            shutil.move(file_path, dup_target)
        else:
            shutil.move(file_path, target)


def clean_movie_names(folder: Path) -> None:
    """Rename movie files inside *folder* to the canonical pattern."""
    logging.info("Cleaning movie names…")
    movie_files = list(folder.iterdir())

    for file_path in tqdm(movie_files, desc="Renaming", unit="file"):
        if file_path.suffix.lower() not in VIDEO_EXTS:
            continue  # Skip non‑video artefacts

        new_path = build_clean_name(file_path)
        if new_path.name != file_path.name:
            logging.debug("%s → %s", file_path.name, new_path.name)
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
    save_paths(
        {
            "Enter the source folder path: ": str(src),
            "Enter the destination folder path: ": str(dst),
        }
    )

    # 1. Gather –> 2. Move –> 3. Clean
    move_files_to_folder(find_video_files(src), dst)
    clean_movie_names(dst)
    logging.info("All done! 🎬")
