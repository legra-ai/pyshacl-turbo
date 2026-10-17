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
from upstream_support.process_launch import Popen


def run(*arguments):
    with Popen(list(map(str, arguments))) as process:
        code = process.wait()
    if code:
        raise subprocess.CalledProcessError(code, arguments)


def output(*arguments):
    with Popen(list(map(str, arguments)), stdout=subprocess.PIPE, text=True) as process:
        value, _ = process.communicate()
        code = process.returncode
    if code:
        raise subprocess.CalledProcessError(code, arguments)
    return value.strip()


def build_archive(archive, output, isolated_output):
    """uv unpacks beside --out-dir, so never build inside a caller's checkout."""
    run("uv", "build", "--wheel", "--python", "3.13", "--out-dir", isolated_output, archive)
    wheels = list(isolated_output.glob("*.whl"))
    if len(wheels) != 1:
        raise RuntimeError(f"Expected exactly one built wheel: {archive}")
    destination = output / wheels[0].name
    shutil.copy2(wheels[0], destination)
    return destination


def checked_revision(source):
    if output("git", "-C", source, "status", "--porcelain", "--untracked-files=all"):
        raise RuntimeError(f"Benchmark wheels require a clean source checkout: {source}")
    return output("git", "-C", source, "rev-parse", "HEAD")


def checkout_source(url, revision, destination):
    run("git", "clone", "--no-checkout", url, destination)
    run("git", "-C", destination, "fetch", "origin", revision)
    run("git", "-C", destination, "checkout", "--detach", revision)
    if checked_revision(destination) != revision:
        raise RuntimeError(f"Source checkout identity mismatch: {destination}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, default=ROOT / "benchmarks/runtime-sources.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    pins = json.loads(args.sources.read_text())
    if pins.keys() != {"rdflib-turbo", "owlrl-turbo"}:
        raise ValueError("Declare both companion source revisions")
    root_revision = checked_revision(ROOT)
    args.output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="turbo-benchmark-build-") as temporary:
        build_root = Path(temporary)
        root_source = build_root / "pyshacl-turbo"
        checkout_source(ROOT, root_revision, root_source)
        sources = {"pyshacl-turbo": root_source}
        for name, revision in pins.items():
            if not re.fullmatch(r"[0-9a-f]{40}", revision):
                raise ValueError("Companion source revisions must be full immutable Git SHAs")
            source = build_root / name
            checkout_source(f"https://github.com/legra-ai/{name}.git", revision, source)
            sources[name] = source
        for name, source in sources.items():
            archives = build_root / f"{name}-archive"
            run("uv", "build", "--sdist", "--python", "3.13", "--out-dir", archives, source)
            artifacts = list(archives.glob("*.tar.gz"))
            if len(artifacts) != 1:
                raise RuntimeError(f"Expected exactly one source archive: {name}")
            # Build from the archive outside any parent checkout's Cargo config.
            build_archive(artifacts[0], args.output, build_root / f"{name}-wheel")
            expected = root_revision if name == "pyshacl-turbo" else pins[name]
            if checked_revision(source) != expected:
                raise RuntimeError(f"Source checkout changed during build: {name}")
    (args.output / "sources.json").write_text(
        json.dumps(
            {
                "pyshacl-turbo": root_revision,
                **pins,
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
