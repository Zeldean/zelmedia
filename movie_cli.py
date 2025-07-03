# ===========================================
# Author: Zeldean
# Project: Movie Manager V3.6
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
load_dotenv()                               # picks up TMDB_API_KEY from .env

import logging
import json
from pathlib import Path
import click

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
        except RuntimeError as e:
            click.echo(f"⚠️  {mv['title']} - {e}")
            meta = {}
        md_path = markdown.save_markdown(mv, meta, out)
        try:
            rel = md_path.relative_to(Path.cwd())
        except ValueError:
            rel = md_path
        click.echo(f"✓ {rel}")


# ─────────────────────── clean-names ─────────────────────
@movie.command("clean-names")
@click.argument("folder", type=click.Path(exists=True, file_okay=False))
def clean_cmd(folder):
    """Rename movies in-place to Nice_Title_(YEAR).ext"""
    rename.clean_movie_names(Path(folder))

# ───────────────────────── main ─────────────────────────
if __name__ == "__main__":
    movie()
