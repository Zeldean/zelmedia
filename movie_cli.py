# ===========================================
# Author: Zeldean
# Project: Movie Manager V3.1
# Date: July 03, 2025
# ===========================================
#   ______      _      _                     
#  |___  /     | |    | |                    
#     / /  ___ | |  __| |  ___   __ _  _ __  
#    / /  / _ \| | / _` | / _ \ / _` || '_ \ 
#   / /__|  __/| || (_| ||  __/| (_| || | | |
#  /_____|\___||_| \__,_| \___| \__,_||_| |_|
# ===========================================

import logging
from pathlib import Path
import json
import click

from movie_manager import scan, markdown, metadata, rename

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

@click.group()
def movie():
    """Movie Manager CLI."""
    pass

@movie.command("scan")
@click.argument("folder", type=click.Path(exists=True, file_okay=False), default=".")
def scan_cmd(folder):
    """List movies in FOLDER."""
    movies = scan.list_movies(folder)
    click.echo(json.dumps(movies, indent=2))

@movie.command("gen-notes")
@click.argument("folder", type=click.Path(exists=True, file_okay=False))
@click.option("--out", "-o", default="notes", show_default=True)
@click.option("--api-key", envvar="OMDB_API_KEY")
def gen_notes_cmd(folder, out, api_key):
    """Create/update a Markdown note per movie."""
    for m in scan.list_movies(folder):
        meta = metadata.fetch_meta(m["title"], m["year"], api_key)
        md_path = markdown.save_markdown(m, meta, out)
        click.echo(f"✓ {md_path.relative_to(Path.cwd())}")

@movie.command("clean-names")
@click.argument("folder", type=click.Path(exists=True, file_okay=False))
def clean_cmd(folder):
    """Rename movies in-place to Nice_Name_(YEAR).ext"""
    rename.clean_movie_names(Path(folder))

if __name__ == "__main__":
    movie()
