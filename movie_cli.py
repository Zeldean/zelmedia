# ===========================================
# Author: Zeldean
# Project: Movie Manager V4.1
# Date: July 03, 2025
# ===========================================
#   ______      _      _                     
#  |___  /     | |    | |                    
#     / /  ___ | |  __| |  ___   __ _  _ __  
#    / /  / _ \| | / _` | / _ \ / _` || '_ \ 
#   / /__|  __/| || (_| ||  __/| (_| || | | |
#  /_____|\___||_| \__,_| \___| \__,_||_| |_|
# ===========================================
from dotenv import load_dotenv
load_dotenv()

import logging
import json
from pathlib import Path
import click
import requests

from movie_manager import scan, markdown, metadata, rename

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

@click.group()
def movie():
    """Movie Manager CLI."""
    pass

# ───────────────────────── scan ─────────────────────────
@movie.command("scan")
@click.argument("folder", type=click.Path(exists=True, file_okay=False), default=".")
def scan_cmd(folder):
    """List movies in FOLDER as JSON."""
    movies = scan.list_movies(folder)
    click.echo(json.dumps(movies, indent=2))

# ─────────────────────── gen-notes ──────────────────────
@movie.command("gen-notes")
@click.argument("folder", type=click.Path(exists=True, file_okay=False))
@click.option("--out", "-o", default="notes", show_default=True,
              type=click.Path(file_okay=False))
def gen_notes(folder, out):
    """
    Create / update one Markdown note per movie in FOLDER
    (metadata from TMDb, key loaded via .env -> TMDB_API_KEY).
    """
    for mv in scan.list_movies(folder):
        try:
            meta = metadata.movie_details(mv["title"], mv["year"])
        except (requests.exceptions.RequestException, RuntimeError) as e:
            click.echo(f"⚠️  {mv['title']} - {e}. Skipping.")
            continue

        if meta is None:                      # no TMDb match
            click.echo(f"⚠️  {mv['title']} - not found on TMDb. Skipping.")
            continue

        md_path = markdown.save_markdown(mv, meta, out)
        click.echo(f"✓ {md_path}")


# ─────────────────────── clean-names ─────────────────────
@movie.command("clean-names")
@click.argument("folder", type=click.Path(exists=True, file_okay=False))
def clean_cmd(folder):
    """Rename movies in-place to Nice_Title_(YEAR).ext"""
    rename.clean_movie_names(Path(folder))

# ───────────────────────── move-files ─────────────────────────
@movie.command("move")
@click.argument("src", type=click.Path(exists=True, file_okay=False))
@click.argument("dst", type=click.Path(file_okay=False))
@click.option("--remember", is_flag=True,
              help="Cache these paths so the next run can omit them.")
def move_cmd(src, dst, remember):
    """
    Move **all** video files from SRC (recursively) to DST (flat),
    preserving original names. Duplicates are prefixed with “[DUP] ”.
    """
    src_p, dst_p = Path(src), Path(dst)
    files = scan.find_video_files(src_p)
    if not files:
        click.echo("No video files found — nothing to move.")
        return

    rename.move_files_to_folder(files, dst_p)
    click.echo(f"✅ Moved {len(files)} files to {dst_p}")

    if remember:
        from movie_manager import paths
        paths.save_paths({
            "last_src": str(src_p),
            "last_dst": str(dst_p),
        })


# ───────────────────────── main ─────────────────────────
if __name__ == "__main__":
    movie()
