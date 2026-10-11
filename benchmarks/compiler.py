"""Compare compiler revisions with the matrix's full-report correctness gate.

Build each revision first. Run serially with PYTHONPATH selecting its installed
package and --source-root selecting its matching checkout. Keep builds and
tests idle while measuring. Each output records source and native-module hashes.
"""

import argparse
import hashlib
import importlib
import json
import platform
import subprocess
import sys
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument("--load-note", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("repeats must be positive")
    root = args.source_root.resolve()
    sys.path.insert(0, str(root / "benchmarks"))
    matrix = importlib.import_module("matrix")
    native = importlib.import_module("pyshacl_turbo._native")
    sources = [root / "Cargo.toml", root / "Cargo.lock", root / "benchmarks/matrix.py"]
    for directory, patterns in [
        ("crates", ("*.rs", "Cargo.toml")),
        ("vendor", ("*.rs", "Cargo.toml")),
        ("python", ("*.py",)),
    ]:
        for pattern in patterns:
            sources.extend((root / directory).rglob(pattern))
    sources.extend((root / "tests/fixtures").glob("pipeline-*.ttl"))
    result = {
        "environment": {
            "date": datetime.now(UTC).isoformat(),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "pyshacl": version("pyshacl"),
            "rdflib": version("rdflib"),
            "pyoxigraph": version("pyoxigraph"),
            "load_note": args.load_note,
        },
        "source_head": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True
        ).strip(),
        "source_root": str(root),
        "package_path": matrix.turbo.__file__,
        "native_path": native.__file__,
        "native_sha256": hashlib.sha256(Path(native.__file__).read_bytes()).hexdigest(),
        "harness_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "source_sha256": {
            str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(sources)
        },
        "repeats": args.repeats,
        "runs": [],
    }
    for specification in [
        ("core", 1000, 1),
        ("shapes", 1000, 10),
        ("shapes", 1000, 100),
        ("shapes", 1000, 1000),
        ("rules", 100, 1),
    ]:
        row = matrix.benchmark(matrix.make_case(*specification), args.repeats)
        result["runs"].append(row)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
        print(
            f"{row['name']}: {row['speedup']:.2f}x; reused {row['reused_speedup']:.2f}x", flush=True
        )


if __name__ == "__main__":
    main()
