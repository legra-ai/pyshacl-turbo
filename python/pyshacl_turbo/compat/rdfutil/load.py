"""``pyshacl.rdfutil.load``: source loading and ``file:`` URI conversion."""

import os
from pathlib import Path, PurePath
from urllib.parse import unquote_to_bytes

from rdflib import URIRef

from pyshacl_turbo.rdf import load_from_source


def path_from_uri(uri: str | URIRef, relative_to: PurePath | None = None) -> Path:
    """Return the path of a ``file:`` URI, with pySHACL's DOS and authority handling."""
    if not uri.startswith("file:"):
        raise ValueError(f"File URI does not start with 'file:': {uri!r}")
    path = str(uri)[5:]
    if path[:3] == "///":
        path = path[2:]
    elif path[:12] == "//localhost/":
        path = path[11:]
    if path[:3] == "///" or (path[:1] == "/" and path[2:3] in ":|"):
        path = path[1:]
    if path[1:2] == "|":
        path = path[:1] + ":" + path[2:]
    result = Path(os.fsdecode(unquote_to_bytes(path)))
    return result if relative_to is None else Path(relative_to).joinpath(result)


__all__ = ["load_from_source", "path_from_uri"]
