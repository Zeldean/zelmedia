"""
Thin wrapper for OMDb (default) or TMDb.  Keeps external HTTP in one place.
"""
import os
import requests

OMDB_URL = "https://www.omdbapi.com/"

def fetch_meta(title: str, year: int, api_key: str | None = None) -> dict:
    """
    Return a dict with at least {"plot": "..."}.
    If *api_key* is None, looks in $OMDB_API_KEY; returns empty dict on failure.
    """
    api_key = api_key or os.getenv("OMDB_API_KEY")
    if not api_key:
        return {}
    params = {"apikey": api_key, "t": title, "y": year}
    try:
        r = requests.get(OMDB_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
    except requests.RequestException:
        return {}

    return {"plot": data.get("Plot", "TODO")}
