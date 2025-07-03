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


def is_unwanted(token: str) -> bool:
    return token.lower() in _UNWANTED_EQUAL


def collapse_underscores(text: str) -> str:
    return re.sub(r"_{2,}", "_", text)


def build_clean_name(original: Path) -> Path:
    stem = original.stem
    if READY_PATTERN.search(stem):
        return original

    # 1. Extract embedded (YEAR)
    year: str | None = None
    m = PAREN_YEAR_SEARCH.search(stem)
    if m:
        year = m.group("year")
        stem = stem[: m.start()] + stem[m.end():]

    # 2. Tokenise & filter
    tokens = re.split(r"[.\-_ ]+", stem)
    title_parts: List[str] = []
    for token in tokens:
        if not token:
            continue
        if year is None and YEAR_RE.fullmatch(token):
            year = token
            continue
        if is_unwanted(token) or any(ch in token for ch in "[]{}()"):
            continue
        if token.isdigit() and len(token) < 4 and year is None:
            title_parts.append(token)
            continue
        title_parts.append(token)

    if not title_parts:
        log.warning("Could not derive title from %s – leaving unchanged", original.name)
        return original

    title = collapse_underscores("_".join(title_parts))
    new_stem = collapse_underscores(f"{title}_({year})" if year else title)
    return original.with_name(new_stem + original.suffix)


# ──────────────────────────────────────────────────────────────
# Bulk actions
# ──────────────────────────────────────────────────────────────
def move_files_to_folder(files: Iterable[Path], destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for file_path in tqdm(files, desc="Moving files", unit="file"):
        target = destination / file_path.name
        if target.exists():
            dup_target = destination / f"[DUP] {file_path.name}"
            log.info("Duplicate detected – moving to %s", dup_target)
            shutil.move(file_path, dup_target)
        else:
            shutil.move(file_path, target)


def clean_movie_names(folder: Path) -> None:
    log.info("Cleaning movie names…")
    for file_path in tqdm(list(folder.iterdir()), desc="Renaming", unit="file"):
        if file_path.suffix.lower() not in VIDEO_EXTS:
            continue
        new_path = build_clean_name(file_path)
        if new_path.name != file_path.name:
            log.debug("%s → %s", file_path.name, new_path.name)
            file_path.rename(new_path)
