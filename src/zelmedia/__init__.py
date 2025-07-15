# src/zelmedia/__init__.py
"""
Public re-exports so callers can simply do:

    from zelmedia import scan, rename, markdown, metadata, links, paths
"""
from importlib import import_module as _imp

_core = "zelmedia.core"

scan      = _imp(f"{_core}.scan")
rename    = _imp(f"{_core}.rename")
markdown  = _imp(f"{_core}.markdown")
metadata  = _imp(f"{_core}.metadata")
paths     = _imp(f"{_core}.paths")
links     = _imp(f"{_core}.links")
constants = _imp(f"{_core}.constants")

__all__ = ["scan", "rename", "markdown", "metadata", "paths", "links", "constants"]
