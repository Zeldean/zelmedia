import json
from pathlib import Path
from typing import Dict

from .constants import PATHS_JSON   # new import

def load_saved_path(prompt: str) -> str | None:
    if not PATHS_JSON.exists():
        return None
    with PATHS_JSON.open("r", encoding="utf-8") as f:
        paths: Dict[str, str] = json.load(f)
    return paths.get(prompt)

def save_paths(paths: Dict[str, str]) -> None:
    # merge with existing keys so we don’t wipe unrelated prompts
    store = {}
    if PATHS_JSON.exists():
        with PATHS_JSON.open("r", encoding="utf-8") as f:
            store = json.load(f)
    store.update(paths)
    with PATHS_JSON.open("w", encoding="utf-8") as f:
        json.dump(store, f, indent=2)
