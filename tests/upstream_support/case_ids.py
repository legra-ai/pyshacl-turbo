"""Stable report identifiers without altering pytest inputs or parametrization."""

from pathlib import Path


def portable_id(nodeid: str, checkout: Path) -> str:
    # URI first, so the filesystem replacement cannot leave a file:// prefix.
    return nodeid.replace(checkout.as_uri() + "/", "").replace(checkout.as_posix() + "/", "")
