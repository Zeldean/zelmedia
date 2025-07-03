import os, requests

TMDB = "https://api.themoviedb.org/3"
API_KEY = os.getenv("TMDB_API_KEY")          # export this before running

def _q(endpoint, **params):
    params["api_key"] = API_KEY
    r = requests.get(f"{TMDB}/{endpoint}", params=params, timeout=30)
    r.raise_for_status()                  # raise HTTP errors
    data = r.json()
    if "status_code" in data and data["status_code"] != 1:
        raise RuntimeError(data["status_message"])
    return data

def movie_details(title, year):
    # 1) search
    hit = _q("search/movie", query=title, year=year)["results"][0]
    mid = hit["id"]

    # 2) full record with collection + similar
    info = _q(f"movie/{mid}", append_to_response="similar,external_ids,credits")
    return {
        "plot": info["overview"],
        "runtime": info["runtime"],
        "genres": [g["name"] for g in info["genres"]],
        "imdb":   info["imdb_id"],
        "poster": f"https://image.tmdb.org/t/p/original{info['poster_path']}",
        "collection": info["belongs_to_collection"] or None,
        "similar": [s["title"] for s in info["similar"]["results"][:10]],
        "series":  _series_from_credits(info["credits"]),
    }

def _series_from_credits(credits):
    # crude heuristic: look for actors whose 'known_for_department' == 'Acting'
    shows = {c["original_name"]
             for c in credits["cast"]
             if c.get("media_type") == "tv"}
    return list(shows)
