"""Reject a shared release planner lacking explicit pure-Python support."""

import argparse
import base64
import hashlib
import json
import re
import subprocess
from pathlib import Path

import yaml

ACTION = "legra-ai/github-actions/.github/actions/prepare-cargo-release@"


def endpoint(reference):
    if not reference.startswith(ACTION) or not re.fullmatch(
        r"[0-9a-f]{40}", reference.removeprefix(ACTION)
    ):
        raise ValueError("Release policy must use the expected immutable shared action")
    return (
        "repos/legra-ai/github-actions/contents/.github/actions/prepare-cargo-release/action.yml?ref="
        + reference.removeprefix(ACTION)
    )


def selected_action(document):
    steps = [step for step in document["jobs"]["prepare"]["steps"] if step.get("id") == "release"]
    if len(steps) != 1:
        raise ValueError("Expected one existing shared release planner")
    step = steps[0]
    reference = step["uses"]
    endpoint(reference)
    if (
        step.get("with", {}).get("manifest-kind") != "uv"
        or step["with"].get("tag-format") != "pep440"
    ):
        raise ValueError("Pure facade release requires manifest-kind=uv and tag-format=pep440")
    return reference


def verify_action(record):
    if record.get("type") != "file" or record.get("encoding") != "base64":
        raise ValueError("Shared release policy metadata is not an original file")
    content = base64.b64decode("".join(record["content"].split()), validate=True)
    if len(content) != record["size"] or len(content) > 32768:
        raise ValueError("Unexpected shared release policy metadata size")
    blob = hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
    if blob != record["sha"]:
        raise ValueError("Shared release policy original blob identity mismatch")
    action = yaml.safe_load(content)
    steps = action.get("runs", {}).get("steps", [])
    if "manifest-kind" not in action.get("inputs", {}) or not any(
        step.get("env", {}).get("RELEASE_MANIFEST_KIND") == "${{ inputs.manifest-kind }}"
        for step in steps
    ):
        raise ValueError(
            "Pinned shared release policy does not support the uv manifest backend; a reviewed published shared policy update is required"
        )
    return action


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workflow", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    reference = selected_action(yaml.safe_load(args.workflow.read_text()))
    record = json.loads(subprocess.check_output(["gh", "api", endpoint(reference)], text=True))
    receipt = {"action": reference, "original_metadata": record, "verified": False}
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n")
    verify_action(record)
    receipt["verified"] = True
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n")


if __name__ == "__main__":
    main()
