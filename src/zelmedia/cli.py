"""
ZelMedia - command-line entry point
"""
from __future__ import annotations

import os
import json
import logging
from pathlib import Path
from typing import List, Tuple

import click
import requests
from dotenv import load_dotenv

# Try loading .env from project root if env var not set
if not os.getenv("TMDB_API_KEY"):
    load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

# ───────────────────────── internal imports ──────────────────────────
from .core import scan, markdown, metadata, rename, links, paths

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# ---------------------------------------------------------------------#
# top-level Click group
# ---------------------------------------------------------------------#
@click.group()
def movie() -> None:
    """ZelMedia CLI - manage movies."""
    pass


# ─────────────────────────── scan ────────────────────────────
@movie.command("scan")
@click.argument("folder", type=click.Path(exists=True, file_okay=False), default=".")
def scan_cmd(folder: str) -> None:
    """List movies in FOLDER (JSON to stdout)."""
    movies = scan.list_movies(folder)
    click.echo(json.dumps(movies, indent=2))


# ───────────────────────── gen-notes ─────────────────────────
@movie.command("gen-notes")
@click.argument("folder", type=click.Path(exists=True, file_okay=False))
@click.option("--out", "-o", default="notes", show_default=True, type=click.Path(file_okay=False))
def gen_notes(folder: str, out: str) -> None:
    """
    Create / update one Markdown note per movie in *FOLDER*.
    Requires TMDB_API_KEY in environment (.env is auto-loaded).
    """
    out_dir = Path(out)
    for mv in scan.list_movies(folder):
        try:
            meta = metadata.movie_details(mv["title"], mv["year"])
        except (requests.exceptions.RequestException, RuntimeError) as e:
            click.echo(f"⚠️  {mv['title']} - {e}. Skipping.")
            continue

        if meta is None:
            click.echo(f"⚠️  {mv['title']} - not found on TMDb. Skipping.")
            continue

        md_path = markdown.save_markdown(mv, meta, out_dir)
        click.echo(f"✓ {md_path}")


# ─────────────────────── clean-names ────────────────────────
@movie.command("clean-names")
@click.argument("folder", type=click.Path(exists=True, file_okay=False))
def clean_cmd(folder: str) -> None:
    """Rename movies in place → Nice_Title_(YEAR).ext"""
    rename.clean_movie_names(Path(folder))


# ─────────────────────── series-rename ──────────────────────
@movie.command("series-rename")
@click.option("-n", "--name", required=True, help="Base series name (e.g., 'Example Show')")
@click.option("--dry-run", is_flag=True, help="Preview changes without executing")
@click.argument("folder", type=click.Path(exists=True, file_okay=False))
def series_rename_cmd(name: str, dry_run: bool, folder: str) -> None:
    """Rename series files → Base_Name_S01E05.ext"""
    rename.clean_series_names(Path(folder), name, dry_run)


# ───────────────────────── move files ───────────────────────
@movie.command("move")
@click.argument("src", required=False, type=click.Path(exists=True, file_okay=False))
@click.argument("dst", required=False, type=click.Path(file_okay=False))
@click.option("--remember", is_flag=True, help="Cache these paths for next run")
def move_cmd(src: str | None, dst: str | None, remember: bool) -> None:
    """
    Move **all** video files from SRC (recursively) to DST (flat).
    Duplicates are renamed “[DUP] filename.ext”.
    If no SRC/DST is passed, tries saved paths.
    """
    if not src:
        src = paths.load_saved_path("last_src")
    if not dst:
        dst = paths.load_saved_path("last_dst")

    if not src or not dst:
        click.echo("Error: source and/or destination not provided or saved.")
        return

    src_p, dst_p = Path(src), Path(dst)
    files = scan.find_video_files(src_p)
    if not files:
        click.echo("No video files found - nothing to move.")
        return

    rename.move_files_to_folder(files, dst_p)
    click.echo(f"✅ Moved {len(files)} files to {dst_p}")

    if remember:
        paths.save_paths({"last_src": str(src_p), "last_dst": str(dst_p)})


# ───────────────────────── YTS links ────────────────────────
@movie.command("yts-links")
@click.option("--out", "-o", type=click.Path(dir_okay=False), help="Write to file instead of stdout")
def yts_links(out: str | None) -> None:
    """Print YTS download links for every *cached* movie."""
    lines: List[str] = [link for *_ , link in links.iter_links()]
    text = "\n".join(lines)
    if out:
        Path(out).write_text(text)
        click.echo(f"✓ wrote {len(lines)} links to {out}")
    else:
        click.echo(text)


# ─────────────── recommendations (unowned) links ────────────
@movie.command("rec-links")
@click.option("--out", "-o", type=click.Path(dir_okay=False), help="Write Markdown grouped in 5-year buckets")
def rec_links(out: str | None) -> None:
    """YTS links for *unowned* recommendations across the cache."""
    entries: List[Tuple[str, str, str]] = list(links.iter_recommended_links())
    if not entries:
        click.echo("No unseen recommendations found.")
        return

    if not out:
        click.echo("\n".join(url for *_ , url in entries))
        return

    # --- group by 5-year buckets -------------------------------------
    buckets: dict[str, List[str]] = {}
    for title, year, url in entries:
        if year == "????":
            bucket = "Unknown Year"
        else:
            y = int(year)
            start = y - (y % 5)
            bucket = f"{start}-{start+4}"
        buckets.setdefault(bucket, []).append(f"- [{title} ({year})]({url})")

    ordered = sorted(buckets.items(), key=lambda kv: (kv[0] == "Unknown Year", kv[0]))

    md_lines: List[str] = []
    for span, lst in ordered:
        md_lines.append(f"## {span}")
        md_lines.extend(lst)
        md_lines.append("")

    Path(out).write_text("\n".join(md_lines))
    click.echo(f"✓ wrote {sum(len(v) for v in buckets.values())} links to {out}")


# ---------------------------------------------------------------------#
if __name__ == "__main__":
    movie()          # pragma: no cover
