"""Public native inference regressions retained during provider ownership migration."""

import pytest
from pyshacl_turbo import compile_shapes, validate
from pyshacl_turbo.graph_abstraction import DataGraph
from pyshacl_turbo.validator import Validator
from rdflib import Graph
from rdflib_turbo import Dataset, Store

DATA = """<urn:validation-inference:child>
    <http://www.w3.org/2000/01/rdf-schema#subPropertyOf> <urn:validation-inference:parent> .
<urn:validation-inference:s> <urn:validation-inference:child> <urn:validation-inference:o> .
"""


SHAPES = """@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix ex: <urn:validation-inference:> .
ex:Shape sh:targetSubjectsOf ex:parent;
    sh:property [sh:path ex:name; sh:minCount 1] .
"""


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
