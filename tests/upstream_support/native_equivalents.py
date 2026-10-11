"""Explicit ports of upstream tests that assert Python implementation details.

These replace neither behavioral failures nor unsupported tests. Their original
IDs and the port name are recorded in the coverage JSON for auditability.
"""


def sparql_function_from_store(module):
    import pyoxigraph as ox
    import pyshacl_turbo as turbo
    from rdflib import Graph, URIRef
    from rdflib.namespace import SH

    store = ox.Store()
    store.load(input=module.data_graph, format=ox.RdfFormat.TURTLE)
    shapes = Graph().parse(data=module.shacl_file, format="turtle")
    shape = URIRef(
        "http://datashapes.org/shasf/tests/expression/advanced.test.shacl#PersonSparqlFunctionShape"
    )
    rule_shape = URIRef(
        "http://datashapes.org/shasf/tests/expression/advanced.test.shacl#PersonRuleShape"
    )
    conforms, report, _ = turbo.validate(
        store, shacl_graph=shapes, advanced=True, use_shapes=[shape, rule_shape]
    )
    # Select the SPARQL constraint and the rule making Jenny a Person. The
    # expression constraint remains excluded. An unregistered function gives an
    # unbound FILTER result and cannot generate these two violations. This tests
    # the native function path instead of spying on a reference Python callback.
    assert not conforms
    assert set(report.objects(None, SH.sourceShape)) == {shape}
    assert set(report.objects(None, SH.sourceConstraintComponent)) == {SH.SPARQLConstraintComponent}
    base = "http://datashapes.org/shasf/tests/expression/advanced.test.data#"
    assert set(report.objects(None, SH.focusNode)) == {URIRef(base + "Bob"), URIRef(base + "Jenny")}


def native_store_adapter(module):
    import pyoxigraph as ox
    import pyshacl_turbo as turbo
    from pyshacl_turbo.rdf import Input, input_graph
    from rdflib import BNode, Graph
    from rdflib.namespace import SH

    store = ox.Store()
    store.add(
        ox.Quad(ox.BlankNode("focus"), ox.NamedNode("urn:p"), ox.Literal(1), ox.NamedNode("urn:g"))
    )
    snapshot = input_graph(store)
    assert isinstance(snapshot, Input)
    assert snapshot.format == "oxigraph-nquads" and snapshot.preserve_ids
    assert set(
        ox.parse(snapshot.source, format=ox.RdfFormat.N_QUADS, rename_blank_nodes=False)
    ) == set(store)
    shapes = Graph().parse(
        data="@prefix sh: <http://www.w3.org/ns/shacl#>. <urn:S> sh:targetSubjectsOf <urn:p>; sh:path <urn:q>; sh:minCount 1.",
        format="turtle",
    )
    conforms, report, _ = turbo.validate(store, shacl_graph=shapes)
    assert not conforms
    assert list(report.objects(None, SH.focusNode)) == [BNode("focus")]
    assert len(store) == 1


PORTS = {
    "test/test_advanced.py::test_advanced_sparql_custom_function": sparql_function_from_store,
    "test/test_rules_oxigraph.py::test_oxigraph_data_graph_wrapper_used": native_store_adapter,
}
