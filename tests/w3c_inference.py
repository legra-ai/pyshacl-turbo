"""Execute original W3C Infer fixtures against an explicitly supplied runner.

This is test infrastructure, not a public inference API. No runner is registered
until the shared native executor exists. Harness tests do not count as W3C passes.
The runner returns the inference graph (only inferred triples), not the union of
that graph with the base graph. Input graphs must remain unchanged on all paths.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from rdflib import RDF, BNode, Graph, URIRef
from rdflib.compare import isomorphic
from suite_harness import MF, SHT
from w3c_grading import Case, CaseType, Document, Grade, Outcome


@dataclass(frozen=True)
class InferenceFixture:
    """One original Infer action and its exact graph or failure expectation."""

    data: Graph
    shapes: Graph
    expected: Graph | None

    @classmethod
    def read(cls, case: Case) -> InferenceFixture:
        if case.case_type is not CaseType.INFER:
            raise ValueError(f"Not an Infer case: {case.id}")
        if case.rdf12_syntax:
            raise ValueError(f"RDF 1.2 input requires a native parser: {case.id}")
        # Discovery projections must never become executable input or expectations.
        document = Document.read(case.path)
        if document.projected:
            raise ValueError(f"RDF 1.2 input requires a native parser: {case.id}")
        manifest = document.graph
        cache = {case.path: manifest}

        def original(path):
            if path.relative_to(case.suite.root).as_posix() not in case.suite.vendored:
                raise ValueError(f"Input outside the pinned inventory: {path}")
            if path not in cache:
                document = Document.read(path)
                if document.projected:
                    raise ValueError(f"RDF 1.2 input requires a native parser: {path}")
                cache[path] = document.graph
            return cache[path]

        data, shapes = (original(path) for path in case.inputs(manifest))
        root = manifest.value(case.node, MF.result, any=False)
        if root == SHT.Failure:
            expected = None
        elif isinstance(root, URIRef) and root != RDF.nil:
            expected = original(case.suite.contained(root))
        elif isinstance(root, BNode) or root == RDF.nil:
            expected = Graph()
            for item in manifest.items(root):
                triple = tuple(manifest.items(item))
                if len(triple) != 3:
                    raise ValueError(f"Expected a three-term result: {case.id}")
                expected.add(triple)
        else:
            raise ValueError(f"Unsupported Infer expectation: {root}")
        return cls(data, shapes, expected)

    def grade(
        self,
        runner: Callable[[Graph, Graph], Graph],
        failure: type[Exception],
    ) -> Grade:
        # bounded: each fixture graph is a single pinned, finite test input.
        before = [(set(graph), set(graph.namespaces())) for graph in (self.data, self.shapes)]
        try:
            actual = runner(self.data, self.shapes)
        except failure:
            grade = Grade(Outcome.PASS if self.expected is None else Outcome.FAIL)
        except Exception as error:  # noqa: BLE001 - never mistake a harness error for failure
            grade = Grade(Outcome.ERROR, type(error).__name__)
        else:
            same = (
                self.expected is not None
                and isinstance(actual, Graph)
                and isomorphic(actual, self.expected)
            )
            grade = Grade(Outcome.PASS if same else Outcome.FAIL)
        after = [(set(graph), set(graph.namespaces())) for graph in (self.data, self.shapes)]
        return Grade(Outcome.FAIL, "input graph mutated") if after != before else grade
