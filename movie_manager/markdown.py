# movie_manager/markdown.py
from pathlib import Path
import yaml, textwrap, requests, json

def slugify(title: str) -> str:
    return "-".join(title.lower().split())

def save_markdown(movie: dict, meta: dict, out_dir="notes") -> Path:
    """
    Write / overwrite a Markdown file with rich sections:
    Synopsis, Cast, More Like This, Related.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    md_path = out / f"{slugify(movie['title'])}.md"

    # ---------- YAML front-matter ----------
    front = {
        "cssclasses": "",
        "tags": ["media/movie", f"media/movie/{movie['year']}", f"media/franchise/{meta.get('franchise','Stand-alone')}"],
        "title": f"{movie['title']} ({movie['year']})",
        "yearReleased": movie["year"],
        "imdbID": meta.get("imdb"),
        "runtime": meta.get("runtime"),
        "genres": meta.get("genres", []),
        "poster": meta.get("poster"),
        "status": "owned",
        "fileName": Path(movie["file"]).name,
    }

    # ---------- body sections ----------
    synopsis = meta.get("plot", "Synopsis not available.")
    cast = "\n".join(f"- {a}" for a in meta.get("cast", [])[:5]) or "- TODO"
    more_like = "\n".join(f"- [[{t.replace(' ', '_')}_(????)]]"
                          for t in meta.get("similar", [])) or "- TODO"
    related = "\n".join(f"- [[{r.replace(' ', '_')}_(????)]]"
                        for r in meta.get("collection_parts", []))
    related_tv = "\n".join(f"- [[TV-Shows/{s}]]" for s in meta.get("series", []))
    related_block = related + ("\n" if related and related_tv else "") + related_tv or "- "

    note = textwrap.dedent(f"""\
    ---
    {yaml.safe_dump(front, sort_keys=False, allow_unicode=True, default_flow_style=False)}---
    # Synopsis
    {synopsis}

    ---
    # Cast (main)
    {cast}

    ---
    # More Like This
    {more_like}

    ---
    # Related
    {related_block}

    ---
    """)
    md_path.write_text(note)
    return md_path
