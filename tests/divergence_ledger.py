"""The one typed ledger of every known Turbo difference, across all suites.

``tests/divergences.toml`` lists each case where Turbo's graded outcome differs
from its baseline: plain pySHACL for every suite, and additionally the W3C
expectation for the SHACL 1.0 gate. Reconciliation is exact in both directions:
an observed difference that is not listed fails, and a listed entry that no
longer differs is stale and fails too.
"""

from __future__ import annotations

import enum
import re
import tomllib
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "tests/divergences.toml"
ADR_PATH = re.compile(r"docs/adr/\d{4}-[a-z0-9-]+\.md")
TRACKING = re.compile(r"https://github\.com/legra-ai/[a-z0-9-]+/(issues|pull)/\d+")


class Suite(enum.StrEnum):
    """Every measured suite whose differences the ledger must account for."""

    W3C_SHACL10 = "w3c-shacl10"
    W3C_SHACL12 = "w3c-shacl12"
    PYSHACL_UPSTREAM = "pyshacl-upstream"
    DIRECT_CONTRACT = "direct-contract"


class Kind(enum.StrEnum):
    """An intentional contract decision, or a gap still to be closed."""

    INTENTIONAL = "intentional"
    GAP = "gap"


class Baseline(enum.StrEnum):
    """What Turbo's outcome is compared against."""

    PYSHACL = "pyshacl"
    W3C_EXPECTATION = "w3c-expectation"


class Origin(enum.StrEnum):
    """Where a graded case comes from; only vendored cases are upstream results."""

    VENDORED = "vendored"
    LOCALLY_CORRECTED = "locally-corrected"
    FIRST_PARTY = "first-party"


@dataclass(frozen=True)
class AdrLink:
    """A repository-relative link to an existing architecture decision record."""

    path: str

    def __post_init__(self) -> None:
        if not ADR_PATH.fullmatch(self.path) or not (ROOT / self.path).is_file():
            raise ValueError(f"Divergence ADR link must name an existing ADR: {self.path!r}")


@dataclass(frozen=True)
class Divergence:
    suite: Suite
    case: str
    kind: Kind
    baseline: Baseline
    reason: str
    adr: AdrLink
    tracking: str | None = None

    FIELDS = frozenset({"suite", "case", "kind", "baseline", "reason", "adr", "tracking"})

    @classmethod
    def parse(cls, row: Mapping[str, object]) -> Divergence:
        if unknown := set(row) - cls.FIELDS:
            raise ValueError(f"Unknown divergence fields: {sorted(unknown)}")
        values = {name: row.get(name) for name in cls.FIELDS}
        for name in cls.FIELDS - {"tracking"}:
            if not isinstance(values[name], str) or not values[name]:
                raise ValueError(f"Divergence field {name!r} must be a non-empty string")
        tracking = values["tracking"]
        if tracking is not None and not (
            isinstance(tracking, str) and TRACKING.fullmatch(tracking)
        ):
            raise ValueError(f"Divergence tracking must be a legra-ai issue or PR: {tracking!r}")
        return cls(
            Suite(str(values["suite"])),
            str(values["case"]),
            Kind(str(values["kind"])),
            Baseline(str(values["baseline"])),
            str(values["reason"]),
            AdrLink(str(values["adr"])),
            tracking,
        )

    @property
    def key(self) -> tuple[Suite, Baseline, str]:
        return self.suite, self.baseline, self.case


class LedgerMismatch(AssertionError):
    """Observed differences and ledger entries disagree."""

    def __init__(self, suite: Suite, baseline: Baseline, unlisted: list[str], stale: list[str]):
        self.unlisted = unlisted
        self.stale = stale
        super().__init__(
            f"{suite} vs {baseline}: unlisted differences {unlisted}; stale entries {stale}"
        )


@dataclass(frozen=True)
class Ledger:
    entries: tuple[Divergence, ...]

    @classmethod
    def load(cls, path: Path = LEDGER) -> Ledger:
        document = tomllib.loads(path.read_text(encoding="utf-8"))
        if set(document) != {"divergence"}:
            raise ValueError("The ledger contains only [[divergence]] tables")
        entries = tuple(Divergence.parse(row) for row in document["divergence"])
        keys = [entry.key for entry in entries]
        if len(keys) != len(set(keys)):
            raise ValueError("Duplicate divergence entries")
        return cls(entries)

    def select(self, suite: Suite, baseline: Baseline = Baseline.PYSHACL) -> dict[str, Divergence]:
        return {
            entry.case: entry
            for entry in self.entries
            if entry.suite is suite and entry.baseline is baseline
        }

    def reconcile(
        self, suite: Suite, observed: Iterable[str], baseline: Baseline = Baseline.PYSHACL
    ) -> None:
        """Require the observed differing case IDs to equal the listed ones exactly."""
        listed = set(self.select(suite, baseline))
        found = set(observed)
        unlisted, stale = sorted(found - listed), sorted(listed - found)
        if unlisted or stale:
            raise LedgerMismatch(suite, baseline, unlisted, stale)

    def counts(self) -> dict[str, dict[str, int]]:
        result: dict[str, dict[str, int]] = {}
        for entry in self.entries:
            row = result.setdefault(entry.suite.value, {kind.value: 0 for kind in Kind})
            row[entry.kind.value] += 1
        return dict(sorted(result.items()))
