"""Caller-visible shapes preparation follows original pySHACL's mutation order."""

import importlib

import pytest
from rdflib import BNode, ConjunctiveGraph, Dataset, Graph, Literal, Namespace
from rdflib.namespace import OWL, RDF, RDFS, SH

EX = Namespace("urn:shapes-bootstrap:")
SYSTEM = (
    (OWL.Class, RDFS.subClassOf, RDFS.Class),
    (OWL.DatatypeProperty, RDFS.subClassOf, RDF.Property),
)


@pytest.fixture(params=("pyshacl", "pyshacl_turbo"), ids=("original", "turbo"))
def implementation(request):
    return importlib.import_module(request.param)


def source_graph(kind):
    if kind.startswith("native"):
        from rdflib_turbo import Graph as NativeGraph
        from rdflib_turbo import StoreDataset

        owner = StoreDataset()
        if kind == "native-dataset":
            return owner, owner.default_graph, owner
        identifier = BNode("selected") if kind.endswith("blank") else EX.selected
        source = NativeGraph(store=owner.store, identifier=identifier)
        return source, source, owner
    if kind.startswith("dataset"):
        source = Dataset(default_union=kind.endswith("on"))
        return source, source.default_graph, source
    if kind == "conjunctive":
        source = ConjunctiveGraph(identifier=EX.selected)
        return source, source.default_context, source
    owner = Dataset()
    identifier = BNode("selected") if kind.endswith("blank") else EX.selected
    source = owner.graph(identifier)
    return source, source, owner


KINDS = (
    "graph",
    "dataset-union-off",
    "dataset-union-on",
    "conjunctive",
    "selected-blank",
    "native-graph",
    "native-blank",
    "native-dataset",
)


@pytest.mark.parametrize("kind", KINDS)
def test_validate_bootstrap_preserves_alias_context_order_and_repeat(
    implementation, kind, monkeypatch
):
    source, selected, _ = source_graph(kind)
    selected.add((EX.shape, SH.targetNode, EX.focus))
    selected.add((EX.shape, SH["class"], EX.Required))
    alias = Graph(store=selected.store, identifier=selected.identifier)
    # An existing triple in another context must not suppress the selected add.
    other = Graph(store=selected.store, identifier=EX.other)
    other.add(SYSTEM[0])
    add = source.store.add
    calls = []  # bounded: exactly two bootstrap writes per validation invocation.

    def observe(triple, context, quoted=False):
        if triple in SYSTEM:
            calls.append((triple, context.identifier, triple in alias))
        return add(triple, context, quoted=quoted)

    monkeypatch.setattr(source.store, "add", observe)
    before = set(alias)
    for _ in range(2):
        result = implementation.validate(Graph(), shacl_graph=source)
        assert result[0] is False
        assert set(alias) == before | set(SYSTEM)
        assert set(other) == {SYSTEM[0]}
    assert calls == [
        (SYSTEM[0], selected.identifier, False),
        (SYSTEM[1], selected.identifier, False),
        (SYSTEM[0], selected.identifier, True),
        (SYSTEM[1], selected.identifier, True),
    ]
    if isinstance(source, Dataset):
        assert source.default_union is True


@pytest.mark.parametrize("kind", ("graph", "dataset-union-off", "native-graph", "native-dataset"))
def test_public_shapes_graph_constructor_publishes_bootstrap(implementation, kind):
    source, selected, _ = source_graph(kind)
    cls = importlib.import_module(implementation.__name__ + ".shapes_graph").ShapesGraph
    wrapper = cls(source)
    assert wrapper.graph is source
    assert all(triple in selected for triple in SYSTEM)
    if isinstance(source, Dataset):
        assert source.default_union is True


@pytest.mark.parametrize("inplace", (False, True))
def test_data_and_shapes_alias_sees_bootstrap_before_target_snapshot(implementation, inplace):
    source = Graph()
    source.add((EX.shape, SH.targetSubjectsOf, RDFS.subClassOf))
    source.add((EX.shape, SH["class"], EX.Required))
    result = implementation.validate(source, shacl_graph=source, inplace=inplace)
    assert result[0] is False
    assert set(result[1].objects(None, SH.focusNode)) == {OWL.Class, OWL.DatatypeProperty}
    assert all(triple in source for triple in SYSTEM)


def test_implicit_shapes_leave_caller_data_without_bootstrap(implementation):
    source = Graph()
    source.add((EX.shape, SH.targetSubjectsOf, RDFS.subClassOf))
    source.add((EX.shape, SH["class"], EX.Required))
    before = set(source)
    assert implementation.validate(source)[0] is True
    assert set(source) == before


def test_public_rules_prepares_caller_shapes(implementation):
    source = Graph()
    source.add((EX.shape, SH.targetNode, EX.focus))
    implementation.shacl_rules(Graph(), shacl_graph=source)
    assert all(triple in source for triple in SYSTEM)


def test_runner_prepares_shapes_once_before_repeated_run(implementation, monkeypatch):
    abstraction = importlib.import_module(implementation.__name__ + ".graph_abstraction")
    source = Graph()
    source.add((EX.shape, SH.targetNode, EX.focus))
    source.add((EX.shape, SH["class"], EX.Required))
    calls = []  # bounded: two construction writes; repeated runner execution adds none.
    add = source.store.add

    def observe(triple, context, quoted=False):
        if triple in SYSTEM:
            calls.append(triple)
        return add(triple, context, quoted=quoted)

    monkeypatch.setattr(source.store, "add", observe)
    runner = implementation.Validator(
        abstraction.DataGraph.from_rdflib_graph(Graph()), shacl_graph=source
    )
    assert calls == list(SYSTEM)
    assert runner.run()[0] is False
    assert runner.run()[0] is False
    assert calls == list(SYSTEM)


@pytest.mark.parametrize("failure", ("missing-file", "data-parse", "inference", "shape-path"))
def test_bootstrap_error_order_matches_original(implementation, failure):
    shapes = Graph()
    shapes.add((EX.shape, SH.targetNode, EX.focus))
    shapes.add((EX.shape, SH.property, EX.property))
    shapes.add((EX.property, SH.path, EX.value))
    data = Graph()
    options = {}
    if failure == "missing-file":
        data = "not valid turtle {"
        options["data_graph_format"] = "turtle"
    elif failure == "data-parse":
        data = "@prefix ex: <urn:parse:> .\nex:subject ex:predicate {"
        options["data_graph_format"] = "turtle"
    elif failure == "inference":
        options["inference"] = "unsupported-inference"
    else:
        shapes.set((EX.property, SH.path, Literal("not a path")))
    # This regression checks preparation ordering; exception-class differences
    # between the original and native parsers are tracked separately.
    errors = {
        "missing-file": FileNotFoundError,
        "data-parse": (SyntaxError, ValueError),
        "inference": (RuntimeError, NotImplementedError),
        "shape-path": (RuntimeError, ValueError),
    }
    with pytest.raises(errors[failure]):
        implementation.validate(data, shacl_graph=shapes, **options)
    assert all(triple in shapes for triple in SYSTEM) is (failure in ("inference", "shape-path"))


def test_explicit_compiled_shapes_preserves_immutable_source_contract():
    from pyshacl_turbo import CompiledShapes

    source = Graph()
    source.add((EX.shape, SH.targetNode, EX.focus))
    source.add((EX.shape, SH["class"], EX.Required))
    before = set(source)
    compiled = CompiledShapes(source)
    assert compiled.validate(Graph())[0] is False
    assert set(source) == before


@pytest.mark.parametrize("operation", ("validate", "shacl_rules"))
def test_document_preparation_does_not_merge_into_discarded_intermediate(operation, monkeypatch):
    import pyshacl_turbo as turbo

    source = Graph()
    source.add((EX.shape, SH.targetNode, EX.focus))
    source.add((EX.shape, SH["class"], EX.Required))

    def reject_unused_merge(*args, **kwargs):
        raise AssertionError("Document input has no caller Graph destination to merge into")

    monkeypatch.setattr(turbo, "merge_graph", reject_unused_merge)
    data = "@prefix ex: <urn:shapes-bootstrap:> .\nex:focus ex:value ex:object ."
    result = getattr(turbo, operation)(data, shacl_graph=source, inference="rdfs", inplace=True)
    if operation == "validate":
        assert result[0] is False
    else:
        assert (EX.focus, EX.value, EX.object) in result
