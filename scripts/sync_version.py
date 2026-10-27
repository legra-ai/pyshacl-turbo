"""Update the pure facade version and lock with native uv, without installation."""

import re
import subprocess
import sys
from pathlib import Path


def synchronize(root, version):
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError(f"Invalid release version: {version!r}")
    for name in ("pyproject.toml", "uv.lock"):
        if not (root / name).is_file():
            raise FileNotFoundError(root / name)
    subprocess.run(["uv", "version", version, "--project", str(root), "--no-sync"], check=True)


if __name__ == "__main__":
    synchronize(Path(__file__).resolve().parents[1], sys.argv[1])
