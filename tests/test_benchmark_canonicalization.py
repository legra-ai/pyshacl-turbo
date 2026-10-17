"""Keep complete RDF equality while avoiding quadratic refinement of anchored reports."""

import importlib.util
from pathlib import Path

from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.compare import isomorphic


def suite():
    path = Path(__file__).resolve().parents[1] / "benchmarks/companions.py"
    spec = importlib.util.spec_from_file_location("workload", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def report(size, prefix):
    sh = Namespace("http://www.w3.org/ns/shacl#")
    graph = Graph()
    root, shape = BNode(prefix + "report"), BNode(prefix + "shape")
    graph.add((root, sh.conforms, Literal(False)))
    graph.add((shape, sh.path, URIRef("urn:name")))
    graph.add((shape, sh.minCount, Literal(1)))
    for i in range(size):
        result = BNode(prefix + str(i))
        graph.add((root, sh.result, result))
        graph.add((result, sh.focusNode, URIRef(f"urn:focus:{i}")))
        graph.add((result, sh.sourceShape, shape))
    return graph


def test_uniquely_anchored_reports_do_not_run_general_blank_node_search(monkeypatch):
    import rdflib.compare

    def unexpected(*args, **kwargs):
        raise AssertionError("Unique anchors should avoid general canonicalization")

    monkeypatch.setattr(rdflib.compare, "to_canonical_graph", unexpected)
    module = suite()
    left, right = report(1000, "a"), report(1000, "renamed")
    assert module.digest_graph(left) == module.digest_graph(right)


def test_canonical_encoding_preserves_shared_nodes_every_edge_and_disconnected_facts():
    module = suite()
    sh = Namespace("http://www.w3.org/ns/shacl#")
    original = report(3, "a")
    changed = report(3, "b")
    result = next(changed.subjects(sh.focusNode, URIRef("urn:focus:0")))
    shared = next(changed.objects(result, sh.sourceShape))
    duplicate = BNode("duplicate")
    changed.remove((result, sh.sourceShape, shared))
    changed.add((result, sh.sourceShape, duplicate))
    for p, o in list(changed.predicate_objects(shared)):
        changed.add((duplicate, p, o))
    assert not isomorphic(original, changed)
    assert module.digest_graph(original) != module.digest_graph(changed)
    changed = report(3, "c")
    changed.add((URIRef("urn:disconnected"), URIRef("urn:p"), Literal("value")))
    assert module.digest_graph(original) != module.digest_graph(changed)


def test_symmetric_blank_nodes_keep_exact_general_canonicalization(monkeypatch):
    import rdflib.compare

    canonicalize = rdflib.compare.to_canonical_graph
    calls = []

    def observed(graph):
        calls.append(graph)
        return canonicalize(graph)

    monkeypatch.setattr(rdflib.compare, "to_canonical_graph", observed)
    module = suite()
    left = Graph().parse(data="_:a <urn:p> _:b. _:b <urn:p> _:a.", format="turtle")
    right = Graph().parse(data="_:x <urn:p> _:y. _:y <urn:p> _:x.", format="turtle")
    assert module.digest_graph(left) == module.digest_graph(right)
    assert len(calls) == 2


def test_self_loops_and_blank_predicates_cannot_alias_other_edges():
    module = suite()
    a, b, predicate = BNode("a"), BNode("b"), URIRef("urn:p")
    self_loop, distinct = Graph(), Graph()
    self_loop.add((a, predicate, a))
    distinct.add((a, predicate, b))
    assert module.digest_graph(self_loop) != module.digest_graph(distinct)
    generalized = Graph()
    generalized.add((a, b, URIRef("urn:o")))
    renamed = Graph()
    renamed.add((BNode("x"), BNode("y"), URIRef("urn:o")))
    assert module.digest_graph(generalized) == module.digest_graph(renamed)


def test_equal_local_signatures_do_not_hide_different_global_connectivity():
    def cycle(size, prefix):
        graph = Graph()
        for i in range(size):
            graph.add(
                (BNode(prefix + str(i)), URIRef("urn:p"), BNode(prefix + str((i + 1) % size)))
            )
        return graph

    one_cycle = cycle(6, "a")
    two_cycles = cycle(3, "b") + cycle(3, "c")
    assert not isomorphic(one_cycle, two_cycles)
    assert suite().digest_graph(one_cycle) != suite().digest_graph(two_cycles)
