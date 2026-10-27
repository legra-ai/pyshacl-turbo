"""Borrowed rule results must be validated before accepting pending writes."""

from contextlib import closing, contextmanager

import pyshacl_turbo as turbo
import pytest
import rdflib_turbo as runtime
from pyshacl_turbo.graph_abstraction import DataGraph
from rdflib import Literal, URIRef

SHAPES = "@prefix sh:<http://www.w3.org/ns/shacl#>. <urn:S> sh:targetNode <urn:s>."
TRIPLE = URIRef("urn:s"), URIRef("urn:p"), Literal("pending")


@pytest.mark.parametrize("factory", [runtime.Graph, runtime.Dataset, runtime.Store])
@pytest.mark.parametrize("inplace", [False, True])
def test_malformed_adapter_output_aborts_before_acceptance(factory, inplace, monkeypatch):
    source = factory()
    accepted = []

    @contextmanager
    def invalid(self, program, settings, requested_inplace):
        assert requested_inplace is inplace
        with self.transaction() as pending:
            pending.parse(data='<urn:s> <urn:p> "pending".', format="turtle")
            yield None, []
            accepted.append(True)

    monkeypatch.setattr(factory, "_expand_shared_shapes", invalid)
    with pytest.raises(RuntimeError, match="expansion result"):
        turbo.shacl_rules(source, shacl_graph=SHAPES, inplace=inplace)
    assert not accepted
    assert len(source) == 0
    source.close()


@pytest.mark.parametrize("invalid_kind", ["same-owner", "wrong-scope", "wrong-category"])
def test_outplace_result_rejects_wrong_owner_scope_or_category(invalid_kind, monkeypatch):
    source = runtime.Graph(identifier=URIRef("urn:selected"))
    if invalid_kind == "same-owner":
        output = runtime.Graph(store=source.store, identifier=source.identifier)
    elif invalid_kind == "wrong-scope":
        output = runtime.Graph(identifier=URIRef("urn:other"))
    else:
        output = runtime.Dataset()
    accepted = []

    @contextmanager
    def invalid(self, program, settings, inplace):
        yield output, []
        accepted.append(True)

    monkeypatch.setattr(runtime.Graph, "_expand_shared_shapes", invalid)
    with pytest.raises(RuntimeError, match="expansion result"):
        turbo.shacl_rules(source, shacl_graph=SHAPES)
    assert not accepted
    source.close()
    output.close()


@pytest.mark.parametrize("factory", [runtime.Graph, runtime.Dataset, runtime.Store])
@pytest.mark.parametrize("inplace", [False, True])
def test_actual_adapter_result_has_independent_owner_or_exact_source(factory, inplace):
    source = factory()
    result = turbo.shacl_rules(source, shacl_graph=SHAPES, inplace=inplace)
    assert (result is source) is inplace
    result.close()
    source.close()


@pytest.mark.parametrize("locked", [False, True])
@pytest.mark.parametrize("inplace", [False, True])
def test_datagraph_adapter_preserves_its_selected_native_view(locked, inplace):
    source = runtime.Dataset()
    view = source.graph(URIRef("urn:selected")) if locked else source
    wrapped = DataGraph(source.store, impl=source, locked_context=view if locked else None)
    result = turbo.shacl_rules(wrapped, shacl_graph=SHAPES, inplace=inplace)
    assert (result is view) is inplace
    if locked:
        assert result.identifier == view.identifier
    result.close()
    source.close()


@pytest.mark.parametrize("inplace", [False, True])
def test_actual_transaction_adapter_returns_transaction_or_independent_store(inplace):
    with runtime.Store() as owner, owner.transaction() as source:
        result = turbo.shacl_rules(source, shacl_graph=SHAPES, inplace=inplace)
        if inplace:
            assert result is source
        else:
            assert isinstance(result, runtime.Store)
            assert result._native is not source._native
            result.close()


def test_native_source_missing_rules_capability_fails_before_writes(monkeypatch):
    with closing(runtime.Graph()) as source:
        source.add(TRIPLE)
        program = turbo.CompiledShapes(SHAPES, advanced=True)
        monkeypatch.setattr(source, "_expand_shared_shapes", None)
        with pytest.raises(RuntimeError, match="does not implement borrowed SHACL rules"):
            program.shacl_rules(source, inplace=True)
        assert set(source) == {TRIPLE}


def test_unrecognized_borrowed_source_cannot_accept_actual_native_rule_output():
    accepted = []
    shapes = (
        SHAPES
        + """
    <urn:S> sh:rule [ a sh:TripleRule; sh:subject sh:this;
                     sh:predicate <urn:derived>; sh:object "done" ].
    """
    )
    with closing(runtime.Graph()) as owner:
        owner.add(TRIPLE)

        class ForeignAdapter:
            def _validate_shared_shapes(self, *args):
                return owner._validate_shared_shapes(*args)

            @contextmanager
            def _expand_shared_shapes(self, program, settings, inplace):
                with owner._expand_shared_shapes(program, settings, inplace) as output:
                    assert isinstance(output[0], runtime.Graph)
                    assert output[0].store.backend._native is not owner.store.backend._native
                    yield output
                    accepted.append(True)

        program = turbo.CompiledShapes(shapes, advanced=True)
        with pytest.raises(RuntimeError, match="expansion result ownership"):
            program.shacl_rules(ForeignAdapter())
        assert not accepted
        assert set(owner) == {TRIPLE}
