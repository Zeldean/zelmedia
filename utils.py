import yaml
from textwrap import indent
from pathlib import Path
import re

MOVIE_RE = re.compile(r"""
    ^(?P<title>.+?)            # everything up to the final _
    _\((?P<year>\d{4})\)       # _(YEAR)
    \.[^.]+$                   # .ext
""", re.VERBOSE)

def list_movies(root: str = "."):
    """Return a list of dicts with title, year, filename for every movie file."""
    movies = []
    for file in Path(root).glob("*.[Mm][Kk][Vv]") | \
               Path(root).glob("*.[Mm][Pp]4")    | \
               Path(root).glob("*.[Aa][Vv][Ii]"):
        m = MOVIE_RE.match(file.name)
        if not m:
            continue                          # skip unexpected names
        title = m.group("title").replace("_", " ")
        movies.append(
            {"title": title,
             "year": int(m.group("year")),
             "file": str(file.resolve())}
        )
    return movies

def save_markdown(movie, meta, out_dir="notes"):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    slug = "-".join(movie["title"].lower().split()) + ".md"
    md_path = out / slug

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
