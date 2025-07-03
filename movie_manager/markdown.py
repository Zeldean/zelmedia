# movie_manager/markdown.py
from pathlib import Path
import yaml, datetime, textwrap

# ──────────────────────────────────────────────────────────────
# helpers
# ──────────────────────────────────────────────────────────────
def title_to_stem(title: str, year: int | str) -> str:
    """Avatar → Avatar_(2009)  ; keeps exact case / spaces→underscores."""
    return f"{title.replace(' ', '_')}_({year})"

def pretty(title: str, year: int | str) -> str:
    return f"{title} ({year})"

def year_from_date(yyyy_mm_dd: str | None) -> str | int:
    if not yyyy_mm_dd:
        return "????"
    return datetime.datetime.fromisoformat(yyyy_mm_dd).year

# ──────────────────────────────────────────────────────────────
def save_markdown(movie: dict, meta: dict, out_dir="notes") -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    stem = title_to_stem(movie["title"], movie["year"])
    md_path = out_dir / f"{stem}.md"

    # ---------- FRONT-MATTER ----------
    front = {
        "cssclasses": "mediaNote",
        "tags": [
            "media/movie",
            f"media/movie/{movie['year']}",
            f"media/franchise/{meta.get('franchise','Stand-alone')}"
        ],
        "title": pretty(movie["title"], movie["year"]),
        "yearReleased": movie["year"],
        "imdbID": meta.get("imdb"),
        "runtime": meta.get("runtime"),
        "genres": meta.get("genres", []),
        "poster": meta.get("poster"),
        "status": "owned",
        "fileName": Path(movie["file"]).name,
    }

    # ---------- CAST ----------
    cast_block = "\n".join(f"- {c}" for c in meta.get("cast", [])[:5]) or "- TODO"

    # ---------- MORE-LIKE-THIS ----------
    # more_like_block = "- TODO"
    # if meta.get("similar"):
    #     ml_items = []
    #     for sim in meta["similar"]:
    #         y = year_from_date(sim.get("release_date"))
    #         stem_sim = title_to_stem(sim["title"], y)
    #         ml_items.append(f"- [[{stem_sim}|{pretty(sim['title'], y)}]]")
    #     more_like_block = "\n".join(ml_items)

    more_like_items = []
    for sim in meta.get("similar", []):
        if isinstance(sim, dict):                   # new robust branch
            title = sim["title"]
            release = sim.get("release_date")
        else:                                       # backwards-compat string
            title = sim
            release = None

        y = year_from_date(release)
        stem_sim = title_to_stem(title, y)
        more_like_items.append(f"- [[{stem_sim}|{pretty(title, y)}]]")

    more_like_block = "\n".join(more_like_items) or "- TODO"

    # ---------- RELATED (collection + TV) ----------
    collection_block = []
    for p in meta.get("collection_parts", []):
        y = year_from_date(p.get("release_date"))
        stem_p = title_to_stem(p["title"], y)
        collection_block.append(f"- [[{stem_p}|{pretty(p['title'], y)}]]")

    tv_block = [f"- [[TV-Shows/{s}]]" for s in meta.get("series", [])]

    related_block = "\n".join(collection_block + tv_block) or "- "

    # ---------- WRITE ----------
    note = textwrap.dedent(f"""\
    ---
    {yaml.safe_dump(front, sort_keys=False, allow_unicode=True)}---
    # Synopsis
    {meta.get('plot', 'Synopsis not available.')}

    ---
    # Cast (main)
    {cast_block}

    ---
    # More Like This
    {more_like_block}

    ---
    # Related
    {related_block}

    ---
    """)
    md_path.write_text(note)
    return md_path
