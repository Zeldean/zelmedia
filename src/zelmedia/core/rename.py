"""
Filename clean-up & move helpers.
"""
from __future__ import annotations

import logging
import re
import shutil
from pathlib import Path
from typing import Iterable, List

from tqdm import tqdm

from .constants import (
    UNWANTED_WORDS, _UNWANTED_EQUAL,
    VIDEO_EXTS, YEAR_RE,
    PAREN_YEAR_SEARCH, READY_PATTERN,
)

log = logging.getLogger(__name__)


# ─────────────────────────── small helpers ────────────────────────────
def is_unwanted(token: str) -> bool:
    """True if *token* is a known rip tag (1080p, BluRay, YTS, etc.)."""
    return token.lower() in _UNWANTED_EQUAL


def collapse_underscores(text: str) -> str:
    """Reduce any run of two or more underscores to a single “_”."""
    return re.sub(r"_{2,}", "_", text)


# ─────────────────────────── core renamer ─────────────────────────────
def build_clean_name(original: Path) -> Path:
    """
    Convert *original* to a nice “Title_(YEAR).ext” Path.

    • If the name already matches READY_PATTERN **and** contains no stray
      “_1_” segment, the original Path is returned unchanged.
    • Removes any “_1_” that sometimes appears in scene releases.
    • Collapses duplicate underscores and strips leading/trailing “_”.
    """
    stem = original.stem

    # already compliant *and* no artefact → nothing to do
    if READY_PATTERN.search(stem) and "_1_" not in stem:
        return original

    # 1. Extract embedded (YEAR)
    year: str | None = None
    m = PAREN_YEAR_SEARCH.search(stem)
    if m:
        year = m.group(0)[1:-1]             # keep the digits only
        stem = stem[:m.start()] + stem[m.end():]

    # 2. Tokenise & filter unwanted fragments
    tokens = re.split(r"[.\-_ ]+", stem)
    title_parts: List[str] = []
    for tok in tokens:
        if not tok:
            continue
        if year is None and YEAR_RE.fullmatch(tok):
            year = tok
            continue
        if is_unwanted(tok) or any(ch in tok for ch in "[]{}()"):
            continue
        if tok.isdigit() and len(tok) < 4 and year is None:
            title_parts.append(tok)         # sequel number
            continue
        title_parts.append(tok)

    if not title_parts:
        log.warning("Could not derive title from %s - leaving unchanged", original.name)
        return original

    # 3. Re-assemble, collapse “_”, strip artefacts
    title = collapse_underscores("_".join(title_parts)).replace("_1_", "_")
    new_stem = collapse_underscores(f"{title}_({year})" if year else title).strip("_")

    return original.with_name(new_stem + original.suffix)


# ─────────────────────────── bulk actions ─────────────────────────────
def move_files_to_folder(files: Iterable[Path], destination: Path) -> None:
    """
    Move *files* into *destination* (non-recursive). Duplicates are
    prefixed with “[DUP] ”.
    """
    destination.mkdir(parents=True, exist_ok=True)
    for file_path in tqdm(files, desc="Moving files", unit="file"):
        target = destination / file_path.name
        if target.exists():
            dup_target = destination / f"[DUP] {file_path.name}"
            log.info("Duplicate detected - moving to %s", dup_target)
            shutil.move(file_path, dup_target)
        else:
            shutil.move(file_path, target)


def clean_movie_names(folder: Path) -> None:
    """
    Rename every video file in *folder* in place using `build_clean_name`.
    """
    log.info("Cleaning movie names…")
    for file_path in tqdm(list(folder.iterdir()), desc="Renaming", unit="file"):
        if file_path.suffix.lower() not in VIDEO_EXTS:
            continue
        new_path = build_clean_name(file_path)
        if new_path.name != file_path.name:
            log.debug("%s → %s", file_path.name, new_path.name)
            file_path.rename(new_path)
