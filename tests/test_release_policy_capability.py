"""Pure releases reject a Cargo-only immutable shared planner before writer access."""

import base64
import hashlib
import importlib.util
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def helper():
    path = ROOT / "scripts/release_policy_capability.py"
    spec = importlib.util.spec_from_file_location("release_policy_capability", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def action_record(body):
    content = body.encode()
    return {
        "type": "file",
        "encoding": "base64",
        "content": base64.b64encode(content).decode(),
        "size": len(content),
        "sha": hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest(),
    }


def test_cargo_only_policy_fails_explicitly_before_any_release_operation():
    with pytest.raises(ValueError, match="does not support the uv manifest backend"):
        helper().verify_action(
            action_record(
                "inputs:\n  token:\n    required: true\nruns:\n  using: composite\n  steps: []\n"
            )
        )


def test_policy_requires_immutable_ref_and_exact_inputs():
    module = helper()
    with pytest.raises(ValueError, match="immutable"):
        module.endpoint("legra-ai/github-actions/.github/actions/prepare-cargo-release@main")
    document = {
        "jobs": {
            "prepare": {
                "steps": [
                    {
                        "id": "release",
                        "uses": "legra-ai/github-actions/.github/actions/prepare-cargo-release@"
                        + "a" * 40,
                        "with": {"manifest-kind": "uv", "tag-format": "pep440"},
                    }
                ]
            }
        }
    }
    assert module.selected_action(document).endswith("@" + "a" * 40)
    document["jobs"]["prepare"]["steps"][0]["with"]["manifest-kind"] = "cargo"
    with pytest.raises(ValueError, match="manifest-kind=uv"):
        module.selected_action(document)


def test_policy_metadata_must_be_original_verified_blob():
    module = helper()
    body = "inputs:\n  manifest-kind:\n    default: cargo\nruns:\n  using: composite\n  steps:\n    - env:\n        RELEASE_MANIFEST_KIND: ${{ inputs.manifest-kind }}\n"
    assert (
        module.verify_action(action_record(body))["inputs"]["manifest-kind"]["default"] == "cargo"
    )
    record = action_record(body)
    record["sha"] = "0" * 40
    with pytest.raises(ValueError, match="blob"):
        module.verify_action(record)


def test_primary_checks_capability_before_requesting_writer_token():
    steps = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())["jobs"]["prepare"][
        "steps"
    ]
    gate = next(
        i
        for i, step in enumerate(steps)
        if "scripts/release_policy_capability.py" in step.get("run", "")
    )
    writer = next(i for i, step in enumerate(steps) if step.get("id") == "writer")
    assert gate < writer
    assert "--with pyyaml==6.0.3" in steps[gate]["run"]
    assert helper().selected_action({"jobs": {"prepare": {"steps": steps}}})
