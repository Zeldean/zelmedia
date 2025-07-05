"""
Generate YTS download URLs from the cached TMDb metadata.
"""

from pathlib import Path
import json, re, unicodedata

# ------------------------------------------------------------------ #
# locate the metadata cache that metadata.py writes/reads
# ------------------------------------------------------------------ #
CACHE_FILE = Path(__file__).with_name("metadata.cache.json")

_slug_re = re.compile(r"[^\w]+")

def _slugify(text: str) -> str:
    """Convert to lowercase ASCII, replace runs of non-word chars with '-'."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return _slug_re.sub("-", text.lower()).strip("-")

# ------------------------------------------------------------------ #
# public iterator
# ------------------------------------------------------------------ #
def iter_links():
    """
    Yield ``(title, year, url)`` tuples for every movie in the cache.
    Falls back gracefully if the cache is missing or empty.
    """
    try:
        cache = json.loads(CACHE_FILE.read_text())
    except FileNotFoundError:
        return  # nothing yet – let caller handle
    except json.JSONDecodeError:
        raise RuntimeError(f"{CACHE_FILE} is corrupted")

    for key in cache.keys():
        # key format is "<title>_<year>"
        if "_" not in key:
            continue
        title, year = key.rsplit("_", 1)
        url = f"https://yts.mx/movies/{_slugify(title)}-{year}"
        yield title, year, url

# ... existing imports and _slugify stay unchanged ...

def _key(title, year):
    """normalise for case-insensitive de-duplication"""
    return f"{title.lower()}_{year}"

def iter_recommended_links():
    """
    Yield (title, year, url) for all movies appearing in any
    `similar` list – excluding ones you already own and duplicates.
    """
    try:
        cache = json.loads(CACHE_FILE.read_text())
    except FileNotFoundError:
        return

    owned_keys = set(k.lower() for k in cache.keys())   # “title_year”
    seen       = set()

    for meta in cache.values():
        for rec in meta.get("similar", []):
            title = rec["title"]
            year  = rec["release_date"][:4] if rec["release_date"] else "????"
            k     = _key(title, year)
            if k in owned_keys or k in seen:
                continue        # already have it or already yielded
            seen.add(k)
            url = f"https://yts.mx/movies/{_slugify(title)}-{year}"
            yield title, year, url
