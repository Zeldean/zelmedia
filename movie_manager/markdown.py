"""
Builds a complete Markdown note from file-info + TMDb metadata.
"""
from pathlib import Path
import yaml, textwrap, datetime

# ── helpers ────────────────────────────────────────────────────────────
def year_from(date_str: str | None) -> int | str:
    if not date_str:
        return "????"
    return datetime.datetime.fromisoformat(date_str).year

def stem(title: str, year) -> str:
    return f"{title.replace(' ', '_')}_({year})"

def pretty(title: str, year) -> str:
    return f"{title} ({year})"

# ── main writer ────────────────────────────────────────────────────────
def save_markdown(movie: dict, meta: dict, out_dir="notes") -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    fname_stem = stem(movie["title"], movie["year"])
    md_path = out / f"{fname_stem}.md"

    front = {
        "cssclasses": "mediaNote",
        "tags": [
            "media/movie",
            f"media/movie/{movie['year']}",
            f"media/franchise/{meta['franchise'].replace(' ', '_')}"
        ],
        "title": pretty(movie["title"], movie["year"]),
        "yearReleased": movie["year"],
        "imdbID": meta["imdb"],
        "runtime": meta["runtime"],
        "genres": meta["genres"],
        "poster": meta["poster"],
        "status": "owned",
        "fileName": Path(movie["file"]).name,
    }

    # Cast
    cast_block = "\n".join(f"- {c}" for c in meta["cast"]) or "- TODO"

    # More-like-this
    ml_block = "\n".join(
        f"- [[{stem(s['title'], year_from(s['release_date']))}|"
        f"{pretty(s['title'], year_from(s['release_date']))}]]"
        for s in meta["similar"]
    ) or "- TODO"

    # Related (collection + TV)
    related_block = "\n".join(
        f"- [[{stem(p['title'], year_from(p['release_date']))}|"
        f"{pretty(p['title'], year_from(p['release_date']))}]]"
        for p in meta["collection_parts"]
    ) or "- "
    if meta["series"]:
        related_block += ("\n" if meta["collection_parts"] else "") + \
            "\n".join(f"- [[TV-Shows/{s}]]" for s in meta["series"])

    # Build note – opening quote at column 0 (no indent)
    note = textwrap.dedent(f"""\
    ---
    {yaml.safe_dump(front, sort_keys=False, allow_unicode=True)}---
    # Synopsis
    {meta['plot']}

    ---
    # Cast (main)
    {cast_block}

    ---
    # More Like This
    {ml_block}

    ---
    # Related
    {related_block}

    ---
    """)
    md_path.write_text(note)
    return md_path
