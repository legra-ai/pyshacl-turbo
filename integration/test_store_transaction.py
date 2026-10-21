"""Cross-wheel validation must use the existing native Store transaction."""

import pytest
from pyshacl_turbo import compile_shapes, validate
from rdflib_turbo import Store

SHAPES = """@prefix sh: <http://www.w3.org/ns/shacl#> .
<urn:S> sh:targetNode <urn:s>; sh:property [sh:path <urn:p>; sh:minCount 1].
"""


def test_compiled_validation_reads_pending_store_writes_without_converting(monkeypatch):
    program = compile_shapes(SHAPES)
    with Store() as store:
        with store.transaction() as transaction:
            transaction.parse(data="<urn:s> <urn:p> 1.")

            def forbidden(*args, **kwargs):
                raise AssertionError("base serialization is forbidden")

            with monkeypatch.context() as patch:
                patch.setattr(Store, "serialize", forbidden)
                patch.setattr(type(transaction), "serialize", forbidden)
                assert program.validate(transaction)[0]
                assert not program.validate(store)[0]
                assert validate(transaction, shacl_graph=SHAPES)[0]
        assert program.validate(store)[0]


@pytest.mark.parametrize("persistent", [False, True])
def test_commit_gate_validates_inference_and_rules_atomically(tmp_path, persistent):
    from rdflib_turbo import ValidationError

    shapes = """@prefix sh: <http://www.w3.org/ns/shacl#> .
    <urn:S> sh:targetClass <urn:Person>;
      sh:rule [a sh:TripleRule; sh:subject sh:this; sh:predicate <urn:derived>; sh:object true];
      sh:property [sh:path <urn:name>; sh:minCount 1]."""
    source = """<urn:Employee> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <urn:Person>.
    <urn:s> a <urn:Employee>."""
    program = compile_shapes(shapes, advanced=True)
    path = tmp_path / "store" if persistent else None
    with Store(path) as store:
        with (
            pytest.raises(ValidationError) as failure,
            store.transaction(shapes=program) as transaction,
        ):
            transaction.parse(data=source).infer(inference="rdfs")
        assert "Conforms: False" in failure.value.text
        assert len(failure.value.report) > 0
        assert len(store) == 0
        with store.transaction(shapes=program, iterate_rules=True) as transaction:
            transaction.parse(data=source + '<urn:s> <urn:name> "Name".').infer(inference="rdfs")
        assert store.query("ASK {<urn:s> a <urn:Person>; <urn:derived> true}")
    if persistent:
        with Store(path) as reopened:
            assert reopened.query("ASK {<urn:s> a <urn:Person>; <urn:derived> true}")


def test_facade_validation_execution_errors_abort_even_if_caught():
    from pyshacl_turbo import ValidationFailure

    program = compile_shapes("""@prefix sh: <http://www.w3.org/ns/shacl#> .
      <urn:S> sh:targetNode <urn:s>; sh:sparql [sh:select "SELECT $this (true AS ?failure) WHERE {}"].""")
    with Store() as store:
        with (
            pytest.raises(RuntimeError, match="closed"),
            store.transaction() as transaction,
        ):
            transaction.parse(data="<urn:s> <urn:p> 1.")
            with pytest.raises(ValidationFailure):
                program.validate(transaction, inplace=True)
        assert len(store) == 0
