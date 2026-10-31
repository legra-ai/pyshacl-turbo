"""Stable report identifiers without altering pytest inputs or parametrization."""

from pathlib import PurePath


def portable_id(nodeid: str, checkout: PurePath) -> str:
    # URI first, so the filesystem replacement cannot leave a file:// prefix.
    return nodeid.replace(checkout.as_uri() + "/", "").replace(checkout.as_posix() + "/", "")
