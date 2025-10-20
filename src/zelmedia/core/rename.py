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
    • Removes any “_1” duplicate counter that sometimes appears in scene releases.
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
        # NEW: drop stray duplicate counters like "_1"
        if tok == "1":
            continue
        if tok.isdigit() and len(tok) < 4 and year is None:
            title_parts.append(tok)         # sequel number (e.g., 2, 3)
            continue
        title_parts.append(tok)

    if not title_parts:
        log.warning("Could not derive title from %s - leaving unchanged", original.name)
        return original

    # 3. Re-assemble, collapse “_”, strip artefacts
    title = collapse_underscores("_".join(title_parts))

    new_stem = collapse_underscores(f"{title}_({year})" if year else title).strip("_")

    # NEW: remove any boundary "_1" that (re)appears after appending the year
    # matches: "_1_", leading "1_", trailing "_1", and "_1(" right before the year
    new_stem = re.sub(r"(^|_)1(?=(_|\(|$))", r"\1", new_stem)
    new_stem = collapse_underscores(new_stem).strip("_")

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

# ───────────────────────────── self-test (20 cases) ─────────────────────────────
# Run with:  python path/to/this_file.py
TEST_CASES: list[tuple[str, str]] = [
    # 1) strip stray "_1" before year
    ("Puss_In_Boots_The_Last_Wish_1_(2022).mp4", "Puss_In_Boots_The_Last_Wish_(2022).mp4"),
    # 2) dot-separated words; keep year; drop bare "1"
    ("The.Matrix.1.1999.mkv", "The_Matrix_(1999).mkv"),
    # 3) keep true sequel numbers when year present
    ("John_Wick_3_2019.mp4", "John_Wick_3_(2019).mp4"),
    # 4) "_(YEAR)_1" tail artifact
    ("Movie_(2020)_1.mp4", "Movie_(2020).mp4"),
    # 5) hyphens, year, and trailing duplicate counter
    ("Some-Film-2021-1.avi", "Some_Film_(2021).avi"),
    # 6) already compliant → unchanged
    ("Ready_Name_(2005).mp4", "Ready_Name_(2005).mp4"),
    # 7) no year → keep as-is (aside from underscore collapsing, if any)
    ("NoYearTitle.mp4", "NoYearTitle.mp4"),
    # 8) sequel number with year
    ("Series_2_2014.mp4", "Series_2_(2014).mp4"),
    # 9) collapse multiple underscores
    ("Weird__Double___Underscore_2018.mp4", "Weird_Double_Underscore_(2018).mp4"),
    # 10) drop bracketed token
    ("Brackets_[EXTRA]_2017.mp4", "Brackets_(2017).mp4"),
    # 11) drop parenthesized non-year token
    ("Hello_(extra)_2011.mkv", "Hello_(2011).mkv"),
    # 12) keep 3-digit sequel-like token when no year yet (then attach year)
    ("Edge.001.2022.mp4", "Edge_001_(2022).mp4"),
    # 13) no year, keep 3-digit sequel-like token
    ("Edge.001.mp4", "Edge_001.mp4"),
    # 14) trim leading/trailing underscores and collapse within
    ("_Leading__and__trailing___underscores_2022__.mp4", "Leading_and_trailing_underscores_(2022).mp4"),
    # 15) compliant simple name
    ("Already_(2015).mkv", "Already_(2015).mkv"),
    # 16) "Title-1-(2016)" → drop the duplicate counter "1"
    ("Title-1-(2016).mp4", "Title_(2016).mp4"),
    # 17) "Name.2008.1" → keep year, drop trailing "1"
    ("Name.2008.1.mkv", "Name_(2008).mkv"),
    # 18) sequels that are real parts should persist
    ("Spider_Man_2_(2004).mp4", "Spider_Man_2_(2004).mp4"),
    # 19) drop parenthesized non-year when no year present
    ("Only_(Extra).mp4", "Only.mp4"),
    # 20) tail duplicate counter without year
    ("Just_1.mp4", "Just.mp4"),
]

def _run_self_test() -> None:
    print("Self-test: build_clean_name\n")
    width = max(len(inp) for inp, _ in TEST_CASES)
    failed = 0
    for src, expected in TEST_CASES:
        got = build_clean_name(Path(src)).name
        ok = (got == expected)
        status = "OK  " if ok else "FAIL"
        print(f"{status}  {src:<{width}}  →  {got}")
        if not ok:
            print(f"      expected: {expected}")
            failed += 1
    total = len(TEST_CASES)
    print(f"\nSummary: {total - failed} passed, {failed} failed, {total} total.")
    raise SystemExit(1 if failed else 0)

