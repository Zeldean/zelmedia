"""
Expose top-level helpers so callers can simply:

    from movie_manager import scan, markdown, rename, metadata
"""
from importlib import import_module as _i

scan      = _i("movie_manager.scan")
markdown  = _i("movie_manager.markdown")
rename    = _i("movie_manager.rename")
paths     = _i("movie_manager.paths")
metadata  = _i("movie_manager.metadata")
constants = _i("movie_manager.constants")

__all__ = ["scan", "markdown", "rename", "paths", "metadata", "constants"]
