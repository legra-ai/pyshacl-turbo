"""Vendor test data from immutable upstream revisions; never execute downloaded code."""

import hashlib
import io
import json
import subprocess
import tarfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
W3C_LICENSE = "W3C Software and Document License"
W3C_LICENSE_URL = "https://www.w3.org/copyright/software-license-2023/"


@dataclass(frozen=True)
class SuiteSource:
    """One pinned upstream revision and the subtree this repository vendors."""

    name: str
    repository: str
    revision: str
    destination: PurePosixPath
    prefix: PurePosixPath | None = None
    extra_files: tuple[tuple[str, str], ...] = ()
    keep: frozenset[str] = frozenset()
    committed_at: str | None = None
    license: str | None = None
    license_url: str | None = None

    @property
    def url(self) -> str:
        return f"https://codeload.github.com/{self.repository}/tar.gz/{self.revision}"

    def target(self, relative: PurePosixPath) -> PurePosixPath | None:
        """Return the vendored path of an archive member, or None when it is not vendored."""
        for source, target in self.extra_files:
            if relative.as_posix() == source:
                return PurePosixPath(target)
        if self.prefix is not None:
            return (
                relative.relative_to(self.prefix) if relative.is_relative_to(self.prefix) else None
            )
        if relative.parts[0] in {"test", "tests"} or relative.as_posix() in self.keep:
            return relative
        return None


SOURCES = (
    SuiteSource(
        "w3c",
        "w3c/data-shapes",
        "07458ebb1ece6addc664636d70b08444a7b66609",
        PurePosixPath("tests/w3c"),
        prefix=PurePosixPath("data-shapes-test-suite/tests"),
    ),
    SuiteSource(
        "w3c12",
        "w3c/data-shapes",
        "0ed3f9b4273c2debba0125a7ed5c9dc3cd4b741c",
        PurePosixPath("tests/w3c12"),
        prefix=PurePosixPath("shacl12-test-suite/tests"),
        extra_files=(
            ("LICENSE.md", "LICENSE.md"),
            ("shacl12-test-suite/README.md", "README.md"),
        ),
        committed_at="2026-11-16T22:33:45Z",
        license=W3C_LICENSE,
        license_url=W3C_LICENSE_URL,
    ),
    SuiteSource(
        "pyshacl",
        "RDFLib/pySHACL",
        "469cca7a22a078b36c167c1e8dadecf5e5ec6c75",
        PurePosixPath("vendor/pyshacl"),
        keep=frozenset({"LICENSE.txt", "FEATURES.md", "pyproject.toml", ".gitmodules"}),
    ),
)


def vendor(source: SuiteSource, content: bytes) -> list[str]:
    files = []
    with tarfile.open(fileobj=io.BytesIO(content), mode="r:gz") as archive:
        for member in archive:
            if not member.isfile():
                continue
            relative = PurePosixPath(*PurePosixPath(member.name).parts[1:])
            if ".." in relative.parts or relative.is_absolute():
                raise ValueError(f"Unsafe archive path: {member.name}")
            target = source.target(relative)
            if target is None:
                continue
            stream = archive.extractfile(member)
            if stream is None:
                raise ValueError(f"Missing archive content: {member.name}")
            destination = ROOT / source.destination / target
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(stream.read())
            files.append(target.as_posix())
    return sorted(files)


def write_checksums(source: SuiteSource, files: list[str]) -> str:
    """Record one SHA-256 line per vendored file, in the coreutils format."""
    base = ROOT / source.destination
    lines = [f"{hashlib.sha256((base / name).read_bytes()).hexdigest()}  {name}" for name in files]
    path = base / "SHA256SUMS"
    path.write_text("\n".join(lines) + "\n")
    return path.relative_to(ROOT).as_posix()


def main() -> None:
    inventory: dict[str, dict[str, object]] = {}
    for source in SOURCES:
        with urllib.request.urlopen(source.url, timeout=60) as response:
            content = response.read()
        files = vendor(source, content)
        entry: dict[str, object] = {"repository": source.repository, "revision": source.revision}
        if source.committed_at is not None:
            entry.update(
                url=source.url,
                committed_at=source.committed_at,
                license=source.license,
                license_url=source.license_url,
                sha256sums=write_checksums(source, files),
            )
        entry["files"] = files
        inventory[source.name] = entry
        if source.name == "pyshacl":
            patch = ROOT / "vendor/pyshacl-issue-70.patch"
            subprocess.run(["git", "apply", str(patch)], cwd=ROOT, check=True)
            entry["local_patches"] = [
                {
                    "path": patch.relative_to(ROOT).as_posix(),
                    "sha256": hashlib.sha256(patch.read_bytes()).hexdigest(),
                }
            ]
        print(f"{source.name}: {len(files)} files from {source.revision}", flush=True)
    (ROOT / "tests/suite-sources.json").write_text(json.dumps(inventory, indent=2) + "\n")


if __name__ == "__main__":
    main()
