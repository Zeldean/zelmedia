"""
TMDb wrapper - returns one dict with everything markdown.py needs.
Requires TMDB_API_KEY in the env (python-dotenv already loads .env).
"""
from pathlib import Path
import os, json, requests, datetime

TMDB = "https://api.themoviedb.org/3"
API_KEY = os.getenv("TMDB_API_KEY")
CACHE_FILE = Path(__file__).with_suffix(".cache.json")

try:
    _CACHE = json.loads(CACHE_FILE.read_text())
except FileNotFoundError:
    _CACHE = {}


# ── small helpers ──────────────────────────────────────────────
def _q(endpoint: str, **params) -> dict:
    params["api_key"] = API_KEY
    r = requests.get(f"{TMDB}/{endpoint}", params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    if "status_code" in data and data["status_code"] != 1:       # TMDb error blob
        raise RuntimeError(data["status_message"])
    return data


def _year(date_str: str | None) -> int | str:
    return "????" if not date_str else datetime.datetime.fromisoformat(date_str).year


# ── main public helper ─────────────────────────────────────────
def movie_details(title: str, year: int | str) -> dict | None:
    """Return a metadata dict or None if the movie isn't found on TMDb."""
    key = f"{title}_{year}"
    if key in _CACHE:
        return _CACHE[key]

    search_hits = _q("search/movie", query=title, year=year)["results"]
    if not search_hits:                         # no match → skip this movie
        return None

    mid = search_hits[0]["id"]

    info = _q(
        f"movie/{mid}",
        append_to_response="recommendations,credits,external_ids"
    )

    # choose recommendations first; fall back to similar if empty
    recs = info["recommendations"]["results"]
    if not recs:
        recs = _q(f"movie/{mid}/similar")["results"]

    data = {
        "plot": info["overview"],
        "runtime": info["runtime"],
        "genres": [g["name"] for g in info["genres"]],
        "imdb": info["external_ids"]["imdb_id"],
        "poster": f"https://image.tmdb.org/t/p/original{info['poster_path']}" if info.get("poster_path") else "",
        "franchise": info["belongs_to_collection"]["name"] if info["belongs_to_collection"] else "Stand-alone",

        # More-like-this list (no cap here; markdown can slice if desired)
        "similar": [
            {"title": m["title"], "release_date": m["release_date"]}
            for m in recs
        ],

        # Top 5 billed cast
        "cast": [
            f"{c['name']} — **{c['character']}**"
            for c in info["credits"]["cast"][:5]
        ],

        # Other movies in the same collection (if any)
        "collection_parts": [
            {"title": p["title"], "release_date": p["release_date"]}
            for p in (_q(f"collection/{info['belongs_to_collection']['id']}")["parts"]
                      if info["belongs_to_collection"] else [])
        ],

        # TV series some cast appear in (very approximate)
        "series": list({
            c["original_name"] for c in info["credits"]["cast"]
            if c.get("media_type") == "tv"
        }),
    }

    _CACHE[key] = data
    CACHE_FILE.write_text(json.dumps(_CACHE, indent=2))
    return data
