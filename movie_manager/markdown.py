from pathlib import Path
import yaml, datetime

def year_from(date: str | None) -> int | str:
    return datetime.datetime.fromisoformat(date).year if date else "????"

def stem(title: str, year) -> str:
    return f"{title.replace(' ', '_')}_({year})"

def pretty(title: str, year) -> str:
    return f"{title} ({year})"

def save_markdown(movie: dict, meta: dict, out_dir="notes") -> Path:
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    note_path = out / f"{stem(movie['title'], movie['year'])}.md"

    # --- front-matter ---------------------------------------------------
    front = {
        "cssclasses": "mediaNote",
        "tags": [
            "media/movie",
            f"media/movie/{movie['year']}",
            f"media/franchise/{meta['franchise'].replace(' ', '_')}"
        ],
        "title": pretty(movie['title'], movie['year']),
        "yearReleased": movie['year'],
        "imdbID": meta['imdb'],
        "runtime": meta['runtime'],
        "genres": meta['genres'],
        "poster": meta['poster'],
        "status": "owned",
        "fileName": Path(movie['file']).name,
    }
    yaml_block = yaml.safe_dump(front, sort_keys=False, allow_unicode=True)

    # --- body sections --------------------------------------------------
    cast = "\n".join(f"- {c}" for c in meta["cast"]) or "- TODO"

    more_like = "\n".join(
        f"- [[{stem(s['title'], year_from(s['release_date']))}"
        f"|{pretty(s['title'], year_from(s['release_date']))}]]"
        for s in meta["similar"]
    ) or "- TODO"

    related_parts = [
        f"- [[{stem(p['title'], year_from(p['release_date']))}"
        f"|{pretty(p['title'], year_from(p['release_date']))}]]"
        for p in meta["collection_parts"]
    ]
    related_tv = [f"- [[TV-Shows/{s}]]" for s in meta["series"]]
    related = "\n".join(related_parts + related_tv) or "- "

    # --- assemble (NO leading spaces) -----------------------------------
    note = (
f"""---
{yaml_block}---
# Synopsis
{meta['plot']}

---
# Cast (main)
{cast}

---
# More Like This
{more_like}

---
# Related
{related}

---
"""
    )

    note_path.write_text(note)
    return note_path
