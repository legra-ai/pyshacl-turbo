"""Release assertions use original metadata, independently of candidate runtime bindings."""

import importlib.util
import os
from pathlib import Path

import pytest


@pytest.fixture
def canonical_release_project(tmp_path):
    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location(
        "release_project_inputs", root / "scripts/release_project_inputs.py"
    )
    authority = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(authority)
    # The existing reader verifies the complete original archive, extracted
    # inventory and immutable Git base. Candidate overrides are never releases.
    metadata = authority.read_release_metadata(root, os.environ)
    for name, body in metadata.items():
        (tmp_path / name).write_bytes(body)
    return tmp_path
