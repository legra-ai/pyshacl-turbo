"""Build exact coordinated companion wheels with uv, before measuring anything."""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from upstream_support.process_launch import install


def run(*arguments):
    subprocess.run(list(map(str, arguments)), check=True)


def build_archive(archive, output, isolated_output):
    """uv unpacks beside --out-dir, so never build inside a caller's checkout."""
    run("uv", "build", "--wheel", "--python", "3.13", "--out-dir", isolated_output, archive)
    wheels = list(isolated_output.glob("*.whl"))
    if len(wheels) != 1:
        raise RuntimeError(f"Expected exactly one built wheel: {archive}")
    destination = output / wheels[0].name
    shutil.copy2(wheels[0], destination)
    return destination


def main():
    install()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, default=ROOT / "benchmarks/runtime-sources.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    pins = json.loads(args.sources.read_text())
    if pins.keys() != {"rdflib-turbo", "owlrl-turbo"}:
        raise ValueError("Declare both companion source revisions")
    args.output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="turbo-benchmark-build-") as temporary:
        build_root = Path(temporary)
        sources = {"pyshacl-turbo": ROOT}
        for name, revision in pins.items():
            if not re.fullmatch(r"[0-9a-f]{40}", revision):
                raise ValueError("Companion source revisions must be full immutable Git SHAs")
            source = build_root / name
            run("git", "clone", "--no-checkout", f"https://github.com/legra-ai/{name}.git", source)
            run("git", "-C", source, "checkout", "--detach", revision)
            actual = subprocess.check_output(
                ["git", "-C", str(source), "rev-parse", "HEAD"], text=True
            ).strip()
            if actual != revision:
                raise RuntimeError(f"Source checkout identity mismatch: {name}")
            sources[name] = source
        for name, source in sources.items():
            archives = build_root / f"{name}-archive"
            run("uv", "build", "--sdist", "--python", "3.13", "--out-dir", archives, source)
            artifacts = list(archives.glob("*.tar.gz"))
            if len(artifacts) != 1:
                raise RuntimeError(f"Expected exactly one source archive: {name}")
            # Build from the archive outside any parent checkout's Cargo config.
            build_archive(artifacts[0], args.output, build_root / f"{name}-wheel")
    (args.output / "sources.json").write_text(
        json.dumps(
            {
                "pyshacl-turbo": subprocess.check_output(
                    ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True
                ).strip(),
                **pins,
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
