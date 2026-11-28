"""``pyshacl.cli_rules``: the ``pyshacl_rules`` rule-expansion command."""

import sys

from pyshacl_turbo.cli import main as _turbo_main


def main(prog: str | None = None) -> None:
    """Expand rules for ``sys.argv`` and exit with pySHACL's status codes."""
    raise SystemExit(_turbo_main(["--rules", *sys.argv[1:]]))


__all__ = ["main"]

if __name__ == "__main__":
    main()
