"""Standalone SHACL bindings supplied by the single native dataset provider."""

from rdflib_turbo._native import shacl as _bindings

SHAPES_BATCH_SIZE = _bindings.SHAPES_BATCH_SIZE
SHACL_ENGINE_FINGERPRINT = _bindings.SHACL_ENGINE_FINGERPRINT
_REGEX_POLICY = _bindings._REGEX_POLICY
CompiledShapes = _bindings.CompiledShapes
TargetData = _bindings.TargetData
ValidationFailure = _bindings.ValidationFailure
ShapeLoadFailure = _bindings.ShapeLoadFailure
ConstraintLoadFailure = _bindings.ConstraintLoadFailure
parse_rdf = _bindings.parse_rdf
ShapesInput = _bindings.ShapesInput
additions = _bindings.additions
infer = _bindings.infer
inoculate = _bindings.inoculate
query = _bindings.query
