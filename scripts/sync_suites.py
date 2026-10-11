"""Vendor test data from immutable upstream revisions; never execute downloaded code."""

import hashlib
import io
import json
import subprocess
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "w3c": ("w3c/data-shapes", "07458ebb1ece6addc664636d70b08444a7b66609"),
    "pyshacl": ("RDFLib/pySHACL", "469cca7a22a078b36c167c1e8dadecf5e5ec6c75"),
}


def main():
    inventory = {}
    for name, (repository, revision) in SOURCES.items():
        url = f"https://codeload.github.com/{repository}/tar.gz/{revision}"
        with urllib.request.urlopen(url, timeout=60) as response:
            content = response.read()
        files = []
        with tarfile.open(fileobj=io.BytesIO(content), mode="r:gz") as archive:
            for member in archive:
                if not member.isfile():
                    continue
                relative = Path(*Path(member.name).parts[1:])
                if ".." in relative.parts or relative.is_absolute():
                    raise ValueError(f"Unsafe archive path: {member.name}")
                if name == "w3c":
                    prefix = Path("data-shapes-test-suite/tests")
                    if not relative.is_relative_to(prefix):
                        continue
                    relative = relative.relative_to(prefix)
                    destination = ROOT / "tests/w3c" / relative
                else:
                    if relative.parts[0] not in {"test", "tests"} and str(relative) not in {
                        "LICENSE.txt",
                        "FEATURES.md",
                        "pyproject.toml",
                        ".gitmodules",
                    }:
                        continue
                    destination = ROOT / "vendor/pyshacl" / relative
                source = archive.extractfile(member)
                if source is None:
                    raise ValueError(f"Missing archive content: {member.name}")
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(source.read())
                files.append(str(relative))
        inventory[name] = {"repository": repository, "revision": revision, "files": sorted(files)}
        if name == "pyshacl":
            patch = ROOT / "vendor/pyshacl-issue-70.patch"
            subprocess.run(["git", "apply", str(patch)], cwd=ROOT, check=True)
            inventory[name]["local_patches"] = [
                {
                    "path": str(patch.relative_to(ROOT)),
                    "sha256": hashlib.sha256(patch.read_bytes()).hexdigest(),
                }
            ]
        print(f"{name}: {len(files)} files from {revision}", flush=True)
    (ROOT / "tests/suite-sources.json").write_text(json.dumps(inventory, indent=2) + "\n")


if __name__ == "__main__":
    main()
