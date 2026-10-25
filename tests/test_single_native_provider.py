"""All three facades must share one native provider and compiled program."""

import gc
import sys
from pathlib import Path

import pyshacl_turbo
from rdflib import Graph as ReferenceGraph
from rdflib.compare import isomorphic
from rdflib_turbo import Graph, _native

SHAPES = """@prefix sh: <http://www.w3.org/ns/shacl#>.
<urn:shape> sh:targetNode <urn:s>;
    sh:property [sh:path <urn:required>; sh:minCount 1].
"""
DATA = "<urn:s> <urn:p> <urn:o>."


def test_standalone_bindings_belong_to_the_dataset_provider():
    assert pyshacl_turbo._native.CompiledShapes is _native.shacl.CompiledShapes
    assert pyshacl_turbo._native._REGEX_POLICY is _native.shacl._REGEX_POLICY
    assert pyshacl_turbo._native._VALUE_COMPARISON_POLICY is _native.shacl._VALUE_COMPARISON_POLICY
    assert pyshacl_turbo.ValidationFailure is _native.shacl.ValidationFailure
    assert _native.SHACL_ENGINE_FINGERPRINT == _native.shacl.SHACL_ENGINE_FINGERPRINT


def test_importing_both_facades_loads_one_product_native_extension():
    extensions = {
        Path(module.__file__).resolve()
        for name, module in tuple(sys.modules.items())
        if name.startswith(("rdflib_turbo.", "pyshacl_turbo."))
        and (getattr(module, "__file__", "") or "").endswith((".so", ".pyd"))
    }
    assert extensions == {Path(_native.__file__).resolve()}


def test_reference_and_native_inputs_reuse_the_same_compiled_program():
    shapes = ReferenceGraph().parse(data=SHAPES, format="turtle")
    program = pyshacl_turbo.compile_shapes(shapes)
    expected = program.validate(ReferenceGraph().parse(data=DATA, format="turtle"))
    source = Graph().parse(data=DATA, format="turtle")
    try:
        owner = source.store.backend._native
        before = set(source)
        actual = program.validate(source)
        assert actual[0] == expected[0] is False
        assert isomorphic(actual[1], expected[1])
        assert actual[2] == expected[2]
        assert source.store.backend._native is owner
        assert set(source) == before
        assert program._shared_program.shares_program(program._native)
    finally:
        source.close()


def test_shared_program_survives_the_standalone_wrapper_and_cache():
    program = pyshacl_turbo.compile_shapes(SHAPES)
    source = Graph().parse(data=DATA, format="turtle")
    try:
        expected = program.validate(source)
        del program._native
        pyshacl_turbo._compile_native.cache_clear()
        gc.collect()
        actual = program.validate(source)
        assert actual[0] == expected[0] is False
        assert isomorphic(actual[1], expected[1])
        assert actual[2] == expected[2]
    finally:
        source.close()
