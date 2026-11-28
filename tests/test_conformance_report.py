"""Published counts and the direct-contract header must not go stale (ADR 0047)."""

import importlib.util
import json
import os
import re
import sys
import tomllib
from collections import Counter
from pathlib import Path

import pytest
from divergence_ledger import Ledger

ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"scripts/{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


report = load_script("conformance_report")
contract = load_script("compare_contract")


def pins():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    pinned = {}
    for requirement in project["dependencies"] + project["optional-dependencies"]["test"]:
        if match := re.fullmatch(r"([a-z-]+)(?:\[[a-z]+\])?==(\S+)", requirement):
            pinned[match[1]] = match[2]
    return project["version"], pinned


def release(version):
    return tuple(int(part) for part in version.split("."))


def within_one_release(measured, current):
    """Allow only the version-only release preparation commit after a measurement."""
    old, new = release(measured), release(current)
    if old == new:
        return True
    if new[:2] == old[:2]:
        return new[2] == old[2] + 1
    if new[0] == old[0]:
        return new[1] == old[1] + 1 and new[2] == 0
    return new == (old[0] + 1, 0, 0)


@pytest.mark.parametrize(
    ("measured", "current", "fresh"),
    [
        ("0.10.2", "0.10.2", True),
        ("0.10.2", "0.10.3", True),
        ("0.10.2", "0.11.0", True),
        ("0.10.2", "1.0.0", True),
        ("0.10.2", "0.10.4", False),
        ("0.10.2", "0.11.1", False),
        ("0.10.2", "0.12.0", False),
        ("0.1.0", "0.10.2", False),
        ("0.10.2", "2.0.0", False),
    ],
)
def test_release_window(measured, current, fresh):
    assert within_one_release(measured, current) is fresh


CANDIDATE_PROVIDER_MARKER = "PYSHACL_TURBO_CANDIDATE_PROVIDER"


class DirectContractFreshness:
    """The committed direct contract names the versions this checkout pins.

    A provider's candidate cohort (rdflib-turbo native coverage) rewrites the
    rdflib-turbo pin to its unpublished build and sets the explicit
    ``PYSHACL_TURBO_CANDIDATE_PROVIDER=1`` marker. The measured provider cannot
    equal that pin, so only the exact provider-version equality is narrowed to
    "a provider is named"; every other assertion stays strict.
    """

    def __init__(self, measured, version, pinned, header, *, candidate_provider):
        self.measured = measured
        self.version = version
        self.pinned = pinned
        self.header = header
        self.candidate_provider = candidate_provider

    @classmethod
    def committed(cls, environment):
        version, pinned = pins()
        return cls(
            json.loads((ROOT / "docs/direct-contract.json").read_text()),
            version,
            pinned,
            (ROOT / "docs/direct-contract.md").read_text(encoding="utf-8").splitlines()[2],
            candidate_provider=environment.get(CANDIDATE_PROVIDER_MARKER) == "1",
        )

    def provider(self):
        measured = self.measured["provider_version"]
        if self.candidate_provider:
            assert re.fullmatch(r"\S+", measured)
            return measured
        assert measured == self.pinned["rdflib-turbo"]
        return measured

    def check(self):
        measured = self.measured
        assert measured["reference_version"] == self.pinned["pyshacl"]
        provider = self.provider()
        assert measured["runtime_authority"]["provider_version"] == provider
        assert measured["runtime_authority"]["facade_version"] == measured["turbo_version"]
        assert within_one_release(measured["turbo_version"], self.version)
        assert self.header == (
            f"Reference: pySHACL {self.pinned['pyshacl']}. Turbo: {measured['turbo_version']}"
            f" with rdflib-turbo {provider}."
        )


def test_direct_contract_header_names_current_versions():
    DirectContractFreshness.committed(os.environ).check()


def freshness(provider, pin, *, candidate_provider, turbo="0.10.8", version="0.10.8"):
    measured = {
        "reference_version": "0.40.2",
        "provider_version": provider,
        "turbo_version": turbo,
        "runtime_authority": {"provider_version": provider, "facade_version": turbo},
    }
    header = f"Reference: pySHACL 0.40.2. Turbo: {turbo} with rdflib-turbo {provider}."
    pinned = {"pyshacl": "0.40.2", "rdflib-turbo": pin}
    return DirectContractFreshness(
        measured, version, pinned, header, candidate_provider=candidate_provider
    )


def test_direct_contract_provider_pin_is_strict_without_the_candidate_marker():
    freshness("0.2.0a43", "0.2.0a43", candidate_provider=False).check()
    with pytest.raises(AssertionError):
        freshness("0.2.0a43", "0.2.0a45", candidate_provider=False).check()


def test_candidate_marker_narrows_only_the_provider_pin():
    freshness("0.2.0a43", "0.2.0a45", candidate_provider=True).check()
    with pytest.raises(AssertionError):
        freshness("", "0.2.0a45", candidate_provider=True).check()
    with pytest.raises(AssertionError):
        freshness("0.2.0a43", "0.2.0a45", candidate_provider=True, turbo="0.10.6").check()
    stale_facade = freshness("0.2.0a43", "0.2.0a45", candidate_provider=True)
    stale_facade.measured["runtime_authority"]["facade_version"] = "0.10.7"
    with pytest.raises(AssertionError):
        stale_facade.check()


@pytest.mark.parametrize(("value", "candidate"), [("1", True), ("0", False), (None, False)])
def test_candidate_marker_is_explicit(value, candidate):
    environment = {} if value is None else {CANDIDATE_PROVIDER_MARKER: value}
    assert DirectContractFreshness.committed(environment).candidate_provider is candidate


def test_direct_contract_counts_and_markdown_do_not_drift():
    measured = json.loads((ROOT / "docs/direct-contract.json").read_text())
    assert measured["summary"] == dict(Counter(row["status"] for row in measured["cases"]))
    rendered = contract.markdown(measured, Ledger.load())
    assert (ROOT / "docs/direct-contract.md").read_text(encoding="utf-8") == rendered
    assert f"Outcomes: {measured['summary']}." in rendered


def test_committed_counts_and_readme_match_a_fresh_measurement():
    committed = json.loads(report.SUMMARY.read_text())
    assert report.collect() == committed
    readme = report.README.read_text(encoding="utf-8")
    assert report.readme_section(readme) == report.render(committed)


def test_readme_section_replacement_is_exact():
    text = f"before\n{report.BEGIN}\nold\n{report.END}\nafter\n"
    assert report.readme_section(text) == f"{report.BEGIN}\nold\n{report.END}"
