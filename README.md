# movie_cli.py  (entry-point only)
import click
from movie_manager import scan, markdown, metadata, rename

@click.group()
def movie():
    """Movie Manager – CLI front-end."""
    ...

@movie.command("scan")
@click.argument("folder", type=click.Path(exists=True, file_okay=False), default=".")
def scan_cmd(folder):
    movies = scan.list_movies(folder)
    click.echo(f"Found {len(movies)} movies")

@movie.command("gen-notes")
@click.argument("folder", type=click.Path(exists=True, file_okay=False))
@click.option("--out", "-o", default="notes")
@click.option("--api-key", envvar="OMDB_API_KEY")
def gen_notes_cmd(folder, out, api_key):
    for m in scan.list_movies(folder):
        meta = metadata.fetch_meta(m["title"], m["year"], api_key) if api_key else {}
        markdown.save_markdown(m, meta, out)
        click.echo(f"✓ {m['title']}")

@movie.command("clean")
@click.argument("folder", type=click.Path(exists=True, file_okay=False))
def clean_cmd(folder):
    rename.clean_movie_names(Path(folder))
