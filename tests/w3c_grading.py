"""Grade pinned W3C SHACL suites for Turbo and plain pySHACL, case by case.

Every manifest entry is discovered and counted. Entry types neither engine
implements are typed not-run cases, never omissions. Validate cases run through
each engine's public ``validate`` with Graph inputs and are graded against the
W3C expectation with the SHACL 1.0 harness's report view. Cases stream one at a
time; no suite-wide graph is retained.
"""

from __future__ import annotations

import enum
import json
import re
from collections import Counter
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import url2pathname

import pyshacl
import pyshacl_turbo
import rdflib
from divergence_ledger import Origin, Suite
from rdflib import RDF, BNode, Graph, Namespace, URIRef
from rdflib.compare import isomorphic
from rdflib.plugins.parsers.notation3 import BadSyntax
from suite_harness import MF, SH, SHT, report_view

TESTS = Path(__file__).resolve().parent
RLT = Namespace("http://www.w3.org/ns/sparql-rl-tests#")
TRIPLE_TERM = "<urn:pyshacl-turbo:w3c12:triple-term>"
# Discovery-only readings of RDF 1.2 Turtle. A projected input is never executed.
RDF12_PROJECTIONS = (
    (re.compile(r"\{\|.*?\|\}", re.DOTALL), ""),
    (re.compile(r"<<\(.*?\)>>", re.DOTALL), TRIPLE_TERM),
    (re.compile(r"(@[A-Za-z]+(?:-[A-Za-z0-9]+)*)--(?:ltr|rtl)\b"), r"\1"),
)


class NotRunReason(enum.StrEnum):
    """Why a discovered case is counted without being executed by either engine."""

    NODE_EXPRESSIONS = "node-expression evaluation is not implemented"
    RULE_INFERENCE = "SHACL 1.2 inference-rule entailment is not implemented"
    SPARQL_RL = "SPARQL-RL rule sets are not implemented"
    RDF12_SYNTAX = "inputs use RDF 1.2 Turtle syntax that RDFLib 7 cannot parse"


class CaseType(enum.Enum):
    """Manifest entry types of the SHACL and SPARQL-RL test suites."""

    VALIDATE = (SHT.Validate, None)
    EVAL_NODE_EXPR = (SHT.EvalNodeExpr, NotRunReason.NODE_EXPRESSIONS)
    INFER = (SHT.Infer, NotRunReason.RULE_INFERENCE)
    SRL_EVAL = (RLT.RulesEvalTest, NotRunReason.SPARQL_RL)
    SRL_POSITIVE_SYNTAX = (RLT.RulesPositiveSyntaxTest, NotRunReason.SPARQL_RL)
    SRL_NEGATIVE_SYNTAX = (RLT.RulesNegativeSyntaxTest, NotRunReason.SPARQL_RL)
    SRL_POSITIVE_WELL_FORMEDNESS = (RLT.RulesPositiveWellFormednessTest, NotRunReason.SPARQL_RL)
    SRL_NEGATIVE_WELL_FORMEDNESS = (RLT.RulesNegativeWellFormednessTest, NotRunReason.SPARQL_RL)
    SRL_POSITIVE_STRATIFICATION = (RLT.RulesPositiveStratificationTest, NotRunReason.SPARQL_RL)
    SRL_NEGATIVE_STRATIFICATION = (RLT.RulesNegativeStratificationTest, NotRunReason.SPARQL_RL)

    def __init__(self, iri: URIRef, reason: NotRunReason | None) -> None:
        self.iri = iri
        self.unsupported = reason

    @classmethod
    def of(cls, iri: object) -> CaseType:
        for member in cls:
            if member.iri == iri:
                return member
        raise ValueError(f"Unknown W3C test type: {iri}")


class Outcome(enum.StrEnum):
    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"
    NOT_RUN = "not-run"


class Relation(enum.StrEnum):
    """How Turbo's graded outcome relates to plain pySHACL's."""

    PARITY = "pyshacl-parity"
    BEYOND = "beyond-pyshacl"
    BEHIND = "behind-pyshacl"
    DIFFERENT = "different-failure"


def parse(text: str, path: Path) -> Graph:
    # Test harness only, called serially: keep intentionally ill-typed literals.
    normalize = rdflib.NORMALIZE_LITERALS
    try:
        rdflib.NORMALIZE_LITERALS = False
        return Graph().parse(data=text, format="turtle", publicID=path.as_uri())
    finally:
        rdflib.NORMALIZE_LITERALS = normalize


@dataclass(frozen=True)
class Document:
    """One parsed suite file; ``projected`` marks a discovery-only RDF 1.2 reading."""

    graph: Graph
    projected: bool

    @classmethod
    def read(cls, path: Path) -> Document:
        text = path.read_text()
        try:
            return cls(parse(text, path), False)
        except BadSyntax:
            for pattern, replacement in RDF12_PROJECTIONS:
                text = pattern.sub(replacement, text)
            return cls(parse(text, path), True)


@dataclass(frozen=True)
class W3cSuite:
    """A vendored W3C test tree and the manifests its discovery starts from."""

    suite: Suite
    directory: str
    manifests: tuple[str, ...]

    @property
    def root(self) -> Path:
        return TESTS / self.directory

    @cached_property
    def vendored(self) -> frozenset[str]:
        sources = json.loads((TESTS / "suite-sources.json").read_text())
        key = {Suite.W3C_SHACL10: "w3c", Suite.W3C_SHACL12: "w3c12"}[self.suite]
        return frozenset(sources[key]["files"])

    def contained(self, uri: object) -> Path:
        parsed = urlparse(str(uri))
        if parsed.scheme != "file" or parsed.netloc:
            raise ValueError(f"Non-local suite input: {uri}")
        path = Path(url2pathname(parsed.path)).resolve()
        if not path.is_relative_to(self.root):
            raise ValueError(f"Suite input escapes pinned tree: {uri}")
        return path

    def discover(self) -> list[Case]:
        pending = [self.root / name for name in self.manifests]
        visited: set[Path] = set()
        cases = []
        while pending:
            path = pending.pop()
            if path in visited:
                continue
            visited.add(path)
            document = Document.read(path)
            graph = document.graph
            pending.extend(self.contained(uri) for uri in graph.objects(None, MF.include))
            for entries in graph.objects(None, MF.entries):
                for node in graph.items(entries):
                    if not isinstance(node, URIRef):
                        raise TypeError(f"Unnamed manifest entry in {path}")
                    cases.append(self.case(document, path, node))
        return sorted(cases, key=lambda case: case.id)

    def case(self, document: Document, path: Path, node: URIRef) -> Case:
        (kind,) = document.graph.objects(node, RDF.type)
        case_type = CaseType.of(kind)
        rdf12 = document.projected
        if case_type is CaseType.VALIDATE and not rdf12:
            files = Case(self, path, node, case_type, False).inputs(document.graph)
            rdf12 = any(Document.read(file).projected for file in files)
        return Case(self, path, node, case_type, rdf12)


W3C_SHACL10 = W3cSuite(Suite.W3C_SHACL10, "w3c", ("manifest.ttl",))
# The 1.2 top manifest omits the SPARQL-RL directories; discover them explicitly.
W3C_SHACL12 = W3cSuite(
    Suite.W3C_SHACL12,
    "w3c12",
    (
        "manifest.ttl",
        "sparql-rl/eval/manifest.ttl",
        "sparql-rl/eval2/manifest.ttl",
        "sparql-rl/examples/manifest.ttl",
        "sparql-rl/stratification/manifest.ttl",
        "sparql-rl/syntax/manifest.ttl",
        "sparql-rl/wellformed/manifest.ttl",
    ),
)


@dataclass(frozen=True)
class Case:
    suite: W3cSuite
    path: Path
    node: URIRef
    case_type: CaseType
    rdf12_syntax: bool

    @property
    def relative(self) -> str:
        return self.path.relative_to(self.suite.root).as_posix()

    @property
    def id(self) -> str:
        return f"{self.relative}::{str(self.node).rsplit('/', 1)[-1]}"

    @property
    def origin(self) -> Origin:
        if self.relative not in self.suite.vendored:
            raise ValueError(f"W3C case outside the pinned inventory: {self.id}")
        return Origin.VENDORED

    @property
    def not_run(self) -> NotRunReason | None:
        if self.case_type.unsupported is not None:
            return self.case_type.unsupported
        return NotRunReason.RDF12_SYNTAX if self.rdf12_syntax else None

    def inputs(self, manifest: Graph) -> list[Path]:
        action = manifest.value(self.node, MF.action, any=False)
        return [
            self.suite.contained(uri)
            for predicate in (SHT.dataGraph, SHT.shapesGraph)
            if (uri := manifest.value(action, predicate, any=False)) is not None
        ]


@dataclass(frozen=True)
class Engine:
    name: str
    validate: Callable[..., tuple[bool, object, str]]
    failure: type[BaseException]


TURBO = Engine("pyshacl-turbo", pyshacl_turbo.validate, pyshacl_turbo.ValidationFailure)
PYSHACL = Engine("pyshacl", pyshacl.validate, pyshacl.errors.ValidationFailure)


ENGINES = (TURBO.name, PYSHACL.name)


@dataclass(frozen=True)
class Grade:
    outcome: Outcome
    detail: str | None = None

    @classmethod
    def grade(cls, case: Case, engine: Engine) -> Grade:
        if (reason := case.not_run) is not None:
            return cls(Outcome.NOT_RUN, reason.name)
        fixture = Document.read(case.path).graph
        expected_root = fixture.value(case.node, MF.result, any=False)
        # Inputs naming the manifest share its parse, so blank-node identity holds.
        cache = {case.path: fixture}
        data, shapes = (cache.setdefault(p, Document.read(p).graph) for p in case.inputs(fixture))
        try:
            conforms, report, _ = engine.validate(data, shacl_graph=shapes)
        except Exception as error:  # noqa: BLE001 - an engine error is a graded outcome
            return cls(Outcome.ERROR, type(error).__name__)
        if expected_root == SHT.Failure:
            failed = not conforms and isinstance(report, engine.failure)
            return cls(Outcome.PASS if failed else Outcome.FAIL)
        if not isinstance(expected_root, BNode):
            raise NotImplementedError(f"W3C expectation: {expected_root}")
        if not isinstance(report, Graph):
            return cls(Outcome.FAIL, "no report graph")
        actual_root = report.value(predicate=RDF.type, object=SH.ValidationReport, any=False)
        if actual_root is None:
            return cls(Outcome.FAIL, "no ValidationReport")
        messages = any(fixture.triples((None, SH.resultMessage, None)))
        details = any(fixture.triples((None, SH.detail, None)))
        actual = report_view(report, actual_root, messages=messages, details=details)
        expected = report_view(fixture, expected_root, messages=messages, details=details)
        same = conforms == bool(fixture.value(expected_root, SH.conforms, any=False))
        return cls(Outcome.PASS if same and isomorphic(actual, expected) else Outcome.FAIL)


@dataclass(frozen=True)
class CaseResult:
    case: Case
    turbo: Grade
    pyshacl: Grade

    @classmethod
    def measure(cls, case: Case) -> CaseResult:
        return cls(case, Grade.grade(case, TURBO), Grade.grade(case, PYSHACL))

    @property
    def relation(self) -> Relation:
        if self.turbo.outcome is self.pyshacl.outcome:
            return Relation.PARITY
        if self.turbo.outcome is Outcome.PASS:
            return Relation.BEYOND
        if self.pyshacl.outcome is Outcome.PASS:
            return Relation.BEHIND
        return Relation.DIFFERENT


@dataclass(frozen=True)
class SuiteTally:
    """Bounded per-type and per-relation counts of one graded suite."""

    types: dict[str, dict[str, dict[str, int]]]
    relations: dict[str, int]
    not_run: dict[str, int]
    differences: tuple[str, ...]

    @classmethod
    def of(cls, results: Iterable[CaseResult]) -> SuiteTally:
        types: dict[str, dict[str, Counter[str]]] = {}
        relations: Counter[str] = Counter()
        not_run: Counter[str] = Counter()
        differences = []
        for result in results:
            column = types.setdefault(
                result.case.case_type.name, {TURBO.name: Counter(), PYSHACL.name: Counter()}
            )
            column[TURBO.name][result.turbo.outcome.value] += 1
            column[PYSHACL.name][result.pyshacl.outcome.value] += 1
            relations[result.relation.value] += 1
            if (reason := result.case.not_run) is not None:
                not_run[reason.name] += 1
            if result.relation is not Relation.PARITY:
                differences.append(result.case.id)
        return cls(
            {
                name: {engine: dict(sorted(c.items())) for engine, c in columns.items()}
                for name, columns in sorted(types.items())
            },
            dict(sorted(relations.items())),
            dict(sorted(not_run.items())),
            tuple(differences),
        )

    def totals(self) -> dict[str, int]:
        return {name: sum(c[PYSHACL.name].values()) for name, c in self.types.items()}

    def engine_totals(self, engine: str) -> dict[str, int]:
        result: Counter[str] = Counter()
        for columns in self.types.values():
            result.update(columns[engine])
        return dict(sorted(result.items()))

    def to_json(self) -> dict[str, object]:
        return {
            "cases": sum(self.totals().values()),
            "origin": {Origin.VENDORED.value: sum(self.totals().values())},
            "types": self.types,
            "outcomes": {engine: self.engine_totals(engine) for engine in ENGINES},
            "relations": self.relations,
            "not_run": self.not_run,
        }


def measure(suite: W3cSuite) -> Iterator[CaseResult]:
    for case in suite.discover():
        if case.origin is not Origin.VENDORED:  # every W3C case is a pinned upstream file
            raise ValueError(f"Unexpected W3C case origin: {case.id}")
        yield CaseResult.measure(case)
