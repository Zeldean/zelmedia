# ZelMedia 📼  
Manage, rename, and catalogue your movie collection from the command-line.

## Getting Started

**First, install the Zel ecosystem:**
```bash
curl -sSL https://raw.githubusercontent.com/Zeldean/zelutil/main/bootstrap-zel.py | python3
```

This sets up ZelUtil and makes all Zel tools available. See the [ZelUtil repository](https://github.com/Zeldean/zelutil) for details.

---

## 1  What is ZelMedia?

| Feature | Details |
|---------|---------|
| **Smart renamer** | Converts noisy scene releases into `Nice_Title_(YEAR).ext)` and detects duplicates. |
| **Mover** | Recursively gathers videos from a “Downloads” folder and flattens them into your library—duplicates are auto-prefixed with `[DUP]`. |
| **Markdown note generator** | Pulls metadata from TMDb and creates a clean note for every movie (synopsis, runtime, genres, poster URL, cast, “More Like This”, etc.). |
| **YTS link builder** | Generates download links for the movies you own—or for recommended titles you don’t own yet. |
| **XDG-compliant cache** | Runtime files live in `~/.local/state/zel/`; the wheel itself remains read-only. |

ZelMedia is one member of the **Zel-suite** (`zeltimer`, `zeljournal`, `zeltask`…)
but works perfectly on its own.

---

## 2  Install

```bash
# in its own pyenv / venv
pip install zelmedia

# development install from source
git clone https://github.com/Zeldean/zelmedia.git
cd zelmedia
pip install -e .
````

> Requires **Python 3.9+**.
> Dependencies: `click`, `requests`, `tqdm`, `python-dotenv`, `PyYAML`.

---

## 3  Quick start

```bash
# List movies as JSON
zelmedia scan ~/Downloads

# Rename files in place
zelmedia clean-names ~/Downloads

# Move everything to flat library folder and remember paths for next run
zelmedia move ~/Downloads ~/Movies --remember

# Generate Markdown notes (TMDB_API_KEY is read from .env)
zelmedia gen-notes ~/Movies -o ~/Notes

# Build a plain list of YTS links from the cache
zelmedia yts-links > links.txt

# Build Markdown of unseen recommendations grouped in 5-year buckets
zelmedia rec-links -o recs.md
```

> Tip: Pair ZelMedia with `zelutil path set media …` so other Zel tools can
> discover the same library location.

---

## 4  Commands in detail

| Command              | Summary                                      | Key options                                         |
| -------------------- | -------------------------------------------- | --------------------------------------------------- |
| `scan [FOLDER]`      | Print a JSON array of `{title, year, file}`. | `--json` *(future)*                                 |
| `clean-names FOLDER` | Rename videos to `Nice_Title_(YEAR).ext`.    | —                                                   |
| `move SRC DST`       | Move all videos from *SRC* → *DST* (flat).   | `--remember` saves these paths in `paths.json`.     |
| `gen-notes FOLDER`   | Create/update Markdown note per movie.       | `-o, --out  NOTES_DIR`                              |
| `yts-links`          | List YTS URLs for every cached movie.        | `-o FILE` writes to file.                           |
| `rec-links`          | YTS URLs for *unowned* recommendations.      | `-o FILE` writes Markdown bucketed by 5-year spans. |

---

## 5  State / cache layout

```
~/.local/state/zel/
    paths.json              # remembered source / destination folders
    metadata.cache.json     # TMDb payloads
```

The directory is created on first run; edit or delete files freely—ZelMedia
will regenerate them. `paths.json` is shared with the rest of the Zel suite via
ZelCandy.

---

## 6  Environment variables

| Variable         | Purpose                                                                                          |
| ---------------- | ------------------------------------------------------------------------------------------------ |
| `TMDB_API_KEY`   | **Required** for `gen-notes`. Put it in `.env` in the working directory or export in your shell. |
| `XDG_STATE_HOME` | Override default state dir (`~/.local/state`).                                                   |

---

## 7  Development workflow

```bash
# activate your pyenv environment
pyenv shell zelutil          # example env

# install in editable mode with test deps
pip install -e .[dev]

pytest -q          # run unit tests
pre-commit run -a  # lint / format
```

* Major refactors should bump **MAJOR** version (e.g., 5.0.0).
* Additive, backward-compatible features bump **MINOR** (x.Y.0).
* Fixes only → **PATCH**.

---

## 8  Roadmap

* `--json` flag for every command (better piping).
* Rich-TUI dashboard in `zelmedia.ui`.
* Windows path support (low priority).
* Optional integration with `zeljournal` to append movie notes directly into the daily note.
