# ===========================================
# Author: Zeldean
# Project: Movie Manager V2.6 (Dry‑Run by default)
# Date: June 26, 2025
# ===========================================
#   ______      _      _                     
#  |___  /     | |    | |                    
#     / /  ___ | |  __| |  ___   __ _  _ __  
#    / /  / _ \| | / _` | / _ \ / _` || '_ \ 
#   / /__|  __/| || (_| ||  __/| (_| || | | |
#  /_____|\___||_| \__,_| \___| \__,_||_| |_|
# ===========================================

"""Movie Manager V2.6 – *dry‑run mode*

Non‑destructive by default: all moves/renames are *printed* while
``DRY_RUN`` is ``True``.

**What’s fixed in 2.6**
----------------------
* _Substring_ matching for rip‑tags – e.g. a token such as ``1-[YTS`` now
  matches ``YTS`` and is removed.
* Added extra tag **"UHD"** + case‑insensitive detection.
* Split tokens on dots, hyphens, underscores *and* spaces so odd bracketed
  parts like ``[YTS.MX]`` get handled.

After validating the output, flip ``DRY_RUN`` to ``False`` to actually move
and rename files.
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

DRY_RUN = True  # ← toggle once you’re happy with the printed actions

# Tag & pattern definitions -------------------------------------------------- #

UNWANTED_WORDS: set[str] = {
    # Resolution / quality
    "1080p", "720p", "2160p", "4k", "4K", "uhd", "UHD",
    # Source / codec
    "BluRay", "WEBRip", "BRrip", "BRRip", "WEB", "HDRip", "DVDRip",
    "x264", "x265", "H264", "H265", "HEVC",
    # Audio / misc
    "AAC", "AAC5", "DDP5", "DDP5_1", "DTS", "Atmos",
    # Scene groups / misc flags
    "YIFY", "YTS", "AM", "MX", "REPACK", "PROPER",
    # Other noise
    "sample", "trailer",
}

VIDEO_EXTS: tuple[str, ...] = (".mp4", ".mkv", ".avi")
YEAR_RE = re.compile(r"^(19|20)\d{2}$")

# Pre‑lowered set for quick membership
_UNWANTED_LOWER = {w.lower() for w in UNWANTED_WORDS}

# --------------------------------------------------------------------------- #
# Core helpers                                                                #
# --------------------------------------------------------------------------- #

def find_video_files(folder: Path) -> list[Path]:
    """Return a list of all *video* files inside *folder* (recursive)."""
    return [p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in VIDEO_EXTS]


def is_unwanted(token: str) -> bool:
    """Return *True* if *token* contains any unwanted word (substring, case‑insensitive)."""
    t = token.lower()
    return any(w in t for w in _UNWANTED_LOWER)


def build_clean_name(original: Path) -> Path:
    """Return a new Path with a cleaned filename according to the spec."""
    # Split on dot/dash/underscore/space so weird tokens like "1-[YTS" break apart
    tokens = re.split(r"[.\-_ ]+", original.stem)

    title_parts: List[str] = []
    year: str | None = None

    for token in tokens:
        if not token:  # skip empties from consecutive separators
            continue
        if YEAR_RE.fullmatch(token):
            year = token
            continue
        if is_unwanted(token):
            continue
        # Skip stray bracketed pieces entirely (e.g. "[YTS")
        if any(ch in token for ch in "[](){}"):
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
    movie_files = list(folder.iterdir())
    for file_path in tqdm(movie_files, desc="Renaming", unit="file"):
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

if __name__ == "__main__":  # pragma: no cover
    src = prompt_path("Enter the source folder path: ")
    dst = prompt_path("Enter the destination folder path: ")
    save_paths({
        "Enter the source folder path: ": str(src),
        "Enter the destination folder path: ": str(dst),
    })

    move_files_to_folder(find_video_files(src), dst)
    clean_movie_names(dst)
    logging.info("Dry‑run complete! Review the actions above. Set DRY_RUN = False when ready.")
