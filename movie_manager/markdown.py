"""
Write one Markdown note per movie with Obsidian-style YAML front-matter.
"""
from pathlib import Path
import yaml


def slugify(title: str) -> str:
    return "-".join(title.lower().split())


def save_markdown(movie: dict, meta: dict | None = None, out_dir: str | Path = "notes") -> Path:
    """
    Create (or overwrite) a .md file for *movie* inside *out_dir*.
    Returns the path created.
    """
    meta = meta or {}
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    md_path = out / f"{slugify(movie['title'])}.md"
    front = {
        "cssclasses": "",
        "tags": ["media/movie"],
        "movieName": movie["title"],
        "movieDescription": meta.get("plot", "TODO"),
        "yearReleased": str(movie["year"]),
        "fileName": Path(movie["file"]).name,
    }

    md_path.write_text(
        f"---\n{yaml.safe_dump(front, sort_keys=False)}---\n"
        "# Genre\n- #media/genre/TODO\n\n"
        "# Related Movies\n- [[TODO]]\n"
    )
    return md_path
