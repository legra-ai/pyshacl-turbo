"""Native validation must infer privately on its existing data owner."""

import decimal
from contextlib import nullcontext
from types import SimpleNamespace

import pytest
from pyshacl import validate as reference_validate
from pyshacl_turbo import Validator, compile_shapes, validate
from pyshacl_turbo.graph_abstraction import DataGraph
from rdflib import BNode, Graph, URIRef
from rdflib.compare import isomorphic
from rdflib_turbo import Dataset, Store, StoreDataset
from rdflib_turbo import Graph as NativeGraph

DATA = """<urn:validation-inference:child>
    <http://www.w3.org/2000/01/rdf-schema#subPropertyOf> <urn:validation-inference:parent> .
<urn:validation-inference:s> <urn:validation-inference:child> <urn:validation-inference:o> .
"""
SHAPES = """@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix ex: <urn:validation-inference:> .
ex:Shape sh:targetSubjectsOf ex:parent;
    sh:property [sh:path ex:name; sh:minCount 1] .
"""


def managed(factory):
    source = factory()
    return source if hasattr(source, "__enter__") else nullcontext(source)


@pytest.mark.parametrize("inference", ["rdfs", "owlrl", "both"])
@pytest.mark.parametrize("factory", [Store, Dataset, NativeGraph, StoreDataset])
def test_native_store_validation_infers_without_mutating_source(inference, factory, monkeypatch):
    reference = Graph().parse(data=DATA, format="turtle")
    shapes = Graph().parse(data=SHAPES, format="turtle")
    assert reference_validate(reference, shacl_graph=shapes)[0]
    if factory in (NativeGraph, StoreDataset):
        # RDFLib serialization itself generates namespace bindings. Apply the
        # same snapshot operation to both graphs before comparing reports.
        reference.serialize()
    expected = reference_validate(reference, shacl_graph=shapes, inference=inference)
    assert not expected[0]
    with managed(factory) as source:
        source.parse(data=DATA)
        before = source.serialize()

        def forbidden(*args, **kwargs):
            raise AssertionError("validation must borrow, not copy or pre-infer the source")

        with monkeypatch.context() as patch:
            for name in ("infer", "copy", "serialize", "to_rdflib"):
                if hasattr(source, name):
                    patch.setattr(source, name, forbidden)
            actual = validate(source, shacl_graph=shapes, inference=inference, inplace=False)
        assert actual[0] == expected[0]
        assert isomorphic(actual[1], expected[1])
        assert source.serialize() == before


@pytest.mark.parametrize("identifier", [URIRef("urn:selected"), BNode("selected")])
@pytest.mark.parametrize("inference", ["rdfs", "owlrl", "both"])
def test_graph_inference_uses_selected_scope_and_pending_writes(identifier, inference):
    shapes = Graph().parse(data=SHAPES, format="turtle")
    source = NativeGraph(identifier=identifier)
    source.parse(data=DATA)
    outside = NativeGraph(store=source.store, identifier=URIRef("urn:outside"))
    outside.add(
        (
            URIRef("urn:validation-inference:s"),
            URIRef("urn:validation-inference:name"),
            URIRef("urn:tempting"),
        )
    )
    before = source.serialize()
    with source.transaction() as pending:
        actual = validate(pending, shacl_graph=shapes, inference=inference, inplace=False)
        assert not actual[0]
        assert pending.serialize() == before
    assert source.serialize() == before
    source.close()


@pytest.mark.parametrize("factory", [Store, Dataset])
def test_report_decoder_failure_does_not_accept_inference(factory, monkeypatch):
    import pyshacl_turbo

    with managed(factory) as source:
        source.parse(data=DATA)
        before = source.serialize()
        shapes = Graph().parse(data=SHAPES, format="turtle")

        def failed_decode(*args, **kwargs):
            raise RuntimeError("synthetic report decoding failure")

        with monkeypatch.context() as patch:
            patch.setattr(pyshacl_turbo, "_graph", failed_decode)
            with pytest.raises(RuntimeError, match="synthetic report decoding failure"):
                validate(source, shacl_graph=shapes, inference="rdfs", inplace=True)
        assert source.serialize() == before


@pytest.mark.parametrize("factory", [Store, Dataset])
def test_inplace_validation_accepts_inferred_facts(factory):
    shapes = Graph().parse(data=SHAPES, format="turtle")
    with managed(factory) as source:
        source.parse(data=DATA)
        assert not validate(source, shacl_graph=shapes, inference="rdfs", inplace=True)[0]
        assert source.query(
            "ASK {<urn:validation-inference:s> <urn:validation-inference:parent> <urn:validation-inference:o>}",
            default_union=True,
        )


def test_ontology_and_rules_preinference_stay_explicitly_unsupported():
    from pyshacl_turbo import shacl_rules

    shapes = Graph().parse(data=SHAPES, format="turtle")
    with Store() as source:
        source.parse(data=DATA)
        with pytest.raises(NotImplementedError, match="ontology"):
            validate(source, shacl_graph=shapes, inference="rdfs", ont_graph=Graph())
        with pytest.raises(NotImplementedError, match="Prepare native inference"):
            shacl_rules(source, shacl_graph=shapes, inference="rdfs")


@pytest.mark.parametrize("factory", [Store, Dataset])
def test_caller_decimal_flags_complete_before_inference_acceptance(factory):
    data = '<urn:s> <urn:p> "1.234567"^^<http://www.w3.org/2001/XMLSchema#double>.'
    observed = []
    for native in [False, True]:
        source = factory().parse(data=data) if native else Graph().parse(data=data, format="turtle")
        with decimal.localcontext() as context:
            context.prec = 3
            context.clear_flags()
            execute = validate if native else reference_validate
            assert execute(source, shacl_graph=Graph(), inference="owlrl", inplace=False)[0]
            observed.append({signal.__name__ for signal, value in context.flags.items() if value})
    assert observed[0] == observed[1] == {"Inexact", "Rounded"}


@pytest.mark.parametrize("factory", [Store, Dataset])
def test_decimal_publication_failure_discards_private_inference(factory, monkeypatch):
    class BrokenFlags:
        def __setitem__(self, key, value):
            raise RuntimeError("synthetic signal publication failure")

    with decimal.localcontext() as context:
        context.prec = 3
        caller = SimpleNamespace(
            **{
                name: getattr(context, name)
                for name in ("prec", "rounding", "Emin", "Emax", "clamp", "traps")
            },
            flags=BrokenFlags(),
        )
        with managed(factory) as source:
            source.parse(
                data='<urn:s> <urn:p> "1.234567"^^<http://www.w3.org/2001/XMLSchema#double>.'
            )
            before = source.serialize()
            with monkeypatch.context() as patch:
                patch.setattr(decimal, "getcontext", lambda: caller)
                with pytest.raises(RuntimeError, match="synthetic signal publication failure"):
                    validate(source, shacl_graph=Graph(), inference="owlrl", inplace=True)
            assert source.serialize() == before


def test_lexical_capture_failure_aborts_prior_pending_transaction_writes(monkeypatch):
    def failed_capture():
        raise RuntimeError("synthetic lexical capture failure")

    with Store() as source:
        with monkeypatch.context() as patch:
            patch.setattr(decimal, "getcontext", failed_capture)
            with (
                pytest.raises(RuntimeError, match="synthetic lexical capture failure"),
                source.transaction() as pending,
            ):
                pending.parse(data=DATA)
                validate(pending, shacl_graph=Graph(), inference="rdfs", inplace=True)
        assert len(source) == 0


def test_compiled_serialized_input_rejects_preinference_before_conversion(monkeypatch):
    import pyshacl_turbo

    program = compile_shapes(SHAPES, shacl_graph_format="turtle")
    source = Graph().parse(data=DATA, format="turtle")
    before = set(source)

    def forbidden(*args, **kwargs):
        raise AssertionError("unsupported pre-inference must fail before serialization")

    monkeypatch.setattr(pyshacl_turbo, "_input", forbidden)
    with pytest.raises(NotImplementedError, match="requires a native source"):
        program.validate(source, inference="rdfs")
    assert set(source) == before


def test_native_dash_preinference_rejects_without_mutating_pending_source():
    shapes = Graph().parse(data=SHAPES, format="turtle")
    with Store() as source:
        source.parse(data=DATA)
        before = source.serialize()
        with pytest.raises(NotImplementedError, match="check_dash_result"):
            validate(
                source,
                shacl_graph=shapes,
                inference="rdfs",
                inplace=True,
                check_dash_result=True,
            )
        assert source.serialize() == before


def test_caller_datagraph_runner_borrows_its_native_owner_on_repeated_runs(monkeypatch):
    import pyshacl_turbo

    class NativeOwner(DataGraph):
        def __init__(self, source):
            self.impl = source

        def is_multigraph(self):
            return False

        def clone(self, *args, **kwargs):
            raise AssertionError("native runner must not clone its data owner")

    source = Dataset().parse(data=DATA)
    before = source.serialize()
    owner = NativeOwner(source)
    runner = Validator(
        owner,
        shacl_graph=Graph().parse(data=SHAPES, format="turtle"),
        options={"inference": "rdfs", "inplace": False},
    )

    def forbidden(*args, **kwargs):
        raise AssertionError("native inference must stay private in the borrowed execution")

    monkeypatch.setattr(pyshacl_turbo, "_prepare_data", forbidden)
    for _ in range(2):
        assert not runner.run()[0]
        assert runner.target_graph is owner
        assert source.serialize() == before
