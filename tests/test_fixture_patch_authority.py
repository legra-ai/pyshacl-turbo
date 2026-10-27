"""The reviewed upstream fixture correction remains an actual source input."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_actual_reviewed_fixture_patch_matches_its_declared_source_authority():
    patches = json.loads((ROOT / "tests/suite-sources.json").read_text())["pyshacl"][
        "local_patches"
    ]
    assert patches == [
        {
            "path": "vendor/pyshacl-issue-70.patch",
            "sha256": "de477823866343abb88851726b7e30e355143231936363d90a544149955fc991",
        }
    ]
    for patch in patches:
        assert hashlib.sha256((ROOT / patch["path"]).read_bytes()).hexdigest() == patch["sha256"]
