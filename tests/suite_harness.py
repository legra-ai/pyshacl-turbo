"""Pinned W3C manifests and comparisons, independent of either validator."""

import json
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlparse

import rdflib
from rdflib import RDF, BNode, Graph, Literal, Namespace, URIRef
from rdflib.compare import isomorphic

ROOT = Path(__file__).parent / "w3c"
SH = Namespace("http://www.w3.org/ns/shacl#")
SHT = Namespace("http://www.w3.org/ns/shacl-test#")
MF = Namespace("http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#")


def parse_fixture(path):
    # Test harness only, called serially. Preserve intentionally ill-typed and
    # noncanonical literals in W3C data instead of repairing the input.
    normalize = rdflib.NORMALIZE_LITERALS
    try:
        rdflib.NORMALIZE_LITERALS = False
        return Graph().parse(path)
    finally:
        rdflib.NORMALIZE_LITERALS = normalize


@dataclass
class Case:
    path: Path
    node: URIRef

    @property
    def id(self):
        return f"{self.path.relative_to(ROOT)}::{str(self.node).rsplit('/', 1)[-1]}"


def local_path(uri):
    parsed = urlparse(str(uri))
    if parsed.scheme != "file" or parsed.netloc:
        raise ValueError(f"Non-local suite input: {uri}")
    path = Path(unquote(parsed.path)).resolve()
    if not path.is_relative_to(ROOT.resolve()):
        raise ValueError(f"Suite input escapes pinned tree: {uri}")
    return path


def cases(section=None):
    pending = [ROOT / (section or "") / "manifest.ttl"]
    visited = set()
    result = []
    while pending:
        path = pending.pop().resolve()
        if path in visited:
            continue
        visited.add(path)
        graph = parse_fixture(path)
        pending.extend(local_path(uri) for uri in graph.objects(None, MF.include))
        for node in graph.subjects(RDF.type, SHT.Validate):
            result.append(Case(path, node))
    return sorted(result, key=lambda case: case.id)


def load(case):
    fixture = parse_fixture(case.path)
    action = fixture.value(case.node, MF.action, any=False)
    cache = {case.path: fixture}

    def read(predicate):
        uri = fixture.value(action, predicate, any=False)
        if uri is None:
            raise ValueError(f"Missing {predicate} in {case.id}")
        path = local_path(uri)
        if path not in cache:
            cache[path] = parse_fixture(path)
        return cache[path]

    return fixture, read(SHT.dataGraph), read(SHT.shapesGraph)


def path_expression(graph, node, active=frozenset()):
    if isinstance(node, URIRef):
        return ["predicate", str(node)]
    if node in active or not isinstance(node, BNode):
        raise ValueError(f"Invalid result path: {node}")
    active = active | {node}
    if (node, RDF.first, None) in graph:
        return ["sequence", [path_expression(graph, n, active) for n in graph.items(node)]]
    for predicate in [
        SH.inversePath,
        SH.alternativePath,
        SH.zeroOrMorePath,
        SH.oneOrMorePath,
        SH.zeroOrOnePath,
    ]:
        value = graph.value(node, predicate, any=False)
        if value is not None:
            if predicate == SH.alternativePath:
                return [
                    str(predicate),
                    [path_expression(graph, n, active) for n in graph.items(value)],
                ]
            return [str(predicate), path_expression(graph, value, active)]
    raise ValueError(f"Unrecognized result path: {node}")


def report_view(graph, root, *, messages, details, preserve_input_ids=True):
    """Retain all report fields; copied input descriptions are not results.

    Optional messages/details are compared when prescribed by the fixture.
    Source/focus/value blank nodes retain input identity for supplied Graphs.
    Independently parsed documents compare those nodes by their descriptions
    and shared references instead. Path definitions compare structurally because
    fixtures can spell the same path twice.
    """
    result = Graph()
    pending = [root]
    seen = set()
    while pending:
        node = pending.pop()
        if node in seen:
            continue
        seen.add(node)
        for _, predicate, obj in graph.triples((node, None, None)):
            if predicate == SH.resultMessage and not messages:
                continue
            if predicate == SH.detail and not details:
                continue
            if predicate == SH.resultPath:
                obj = Literal(json.dumps(path_expression(graph, obj)))
            elif predicate in {SH.sourceShape, SH.focusNode, SH.value, SH.sourceConstraint}:
                if isinstance(obj, BNode):
                    if preserve_input_ids:
                        obj = URIRef(f"urn:input-bnode:{obj}")
                    else:
                        pending.append(obj)
            elif isinstance(obj, BNode):
                pending.append(obj)
            result.add((node, predicate, obj))
    return result


def compare(case, validate, *, documents=False):
    fixture, data, shapes = load(case)
    if documents:
        action = fixture.value(case.node, MF.action, any=False)
        data = local_path(fixture.value(action, SHT.dataGraph, any=False))
        shapes = local_path(fixture.value(action, SHT.shapesGraph, any=False))
    expected_root = fixture.value(case.node, MF.result, any=False)
    if expected_root == SHT.Failure:
        import pyshacl_turbo

        conforms, result, _ = validate(data, shacl_graph=shapes)
        assert not conforms and isinstance(result, pyshacl_turbo.ValidationFailure), (
            "Expected a SHACL ValidationFailure"
        )
        return
    if not isinstance(expected_root, BNode):
        raise NotImplementedError(f"W3C failure expectation: {expected_root}")
    conforms, report, _ = validate(data, shacl_graph=shapes)
    actual_root = report.value(predicate=RDF.type, object=SH.ValidationReport, any=False)
    if actual_root is None:
        raise AssertionError("No ValidationReport returned")
    messages = any(fixture.triples((None, SH.resultMessage, None)))
    details = any(fixture.triples((None, SH.detail, None)))
    actual = report_view(
        report,
        actual_root,
        messages=messages,
        details=details,
        preserve_input_ids=not documents,
    )
    expected = report_view(
        fixture,
        expected_root,
        messages=messages,
        details=details,
        preserve_input_ids=not documents,
    )
    assert conforms == bool(fixture.value(expected_root, SH.conforms, any=False))
    assert isomorphic(actual, expected), (
        actual.serialize(format="turtle"),
        expected.serialize(format="turtle"),
    )
