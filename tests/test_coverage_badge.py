"""Coverage badges must describe measured Python lines and branches honestly."""

import importlib.util
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "coverage_badge", Path(__file__).resolve().parents[1] / "scripts/coverage_badge.py"
)


@pytest.fixture
def badge():
    module = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(module)
    return module


def report():
    return {
        "meta": {"branch_coverage": True},
        "totals": {
            "num_statements": 80,
            "covered_lines": 70,
            "num_branches": 20,
            "covered_branches": 5,
        },
    }


def test_badge_includes_uncovered_branches_in_its_percentage(badge):
    root = ET.fromstring(badge.render_badge(report()))
    assert root.attrib["aria-label"] == "Python coverage: 75.0%"
    assert "75.0%" in "".join(root.itertext())


def test_badge_does_not_round_partial_coverage_to_100_percent(badge):
    observed = report()
    observed["totals"].update(
        num_statements=10000, covered_lines=9999, num_branches=0, covered_branches=0
    )
    root = ET.fromstring(badge.render_badge(observed))
    assert root.attrib["aria-label"] == "Python coverage: 99.9%"


def test_badge_accepts_complete_coverage(badge):
    observed = report()
    observed["totals"].update(covered_lines=80, covered_branches=20)
    root = ET.fromstring(badge.render_badge(observed))
    assert root.attrib["aria-label"] == "Python coverage: 100.0%"


@pytest.mark.parametrize(
    "change",
    [
        lambda r: r["meta"].update(branch_coverage=False),
        lambda r: r.pop("totals"),
        lambda r: r["totals"].pop("covered_branches"),
        lambda r: r["totals"].update(covered_lines=-1),
        lambda r: r["totals"].update(covered_lines=81),
        lambda r: r["totals"].update(covered_branches=21),
        lambda r: r["totals"].update(covered_lines=True),
        lambda r: r["totals"].update(covered_lines=70.5),
        lambda r: r["totals"].update(covered_branches=float("nan")),
        lambda r: r["totals"].update(
            num_statements=0, covered_lines=0, num_branches=0, covered_branches=0
        ),
    ],
)
def test_badge_rejects_missing_or_invalid_measurements(badge, change):
    observed = report()
    change(observed)
    with pytest.raises(ValueError):
        badge.render_badge(observed)
