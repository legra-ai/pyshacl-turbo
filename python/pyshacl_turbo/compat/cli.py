"""``pyshacl.cli``: the ``pyshacl`` validation command."""

import sys

from pyshacl_turbo.cli import main as _turbo_main


def main(prog: str | None = None) -> None:
    """Run the command with ``sys.argv`` and exit with pySHACL's status codes."""
    raise SystemExit(_turbo_main(sys.argv[1:]))


__all__ = ["main"]

if __name__ == "__main__":
    main()
