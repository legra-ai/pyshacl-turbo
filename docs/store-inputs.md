# Store inputs

Pass an existing PyOxigraph Store to the normal validation or rule API:

```python
from pyoxigraph import RdfFormat, Store
from pyshacl_turbo import compile_shapes, validate

store = Store()
store.load(path="data.trig", format=RdfFormat.TRIG)

conforms, report, text = validate(
    store, shacl_graph="shapes.ttl", advanced=True, inference="rdfs"
)

program = compile_shapes("shapes.ttl", advanced=True)
conforms, report, text = program.validate(store)
```

Store inputs work for data, shapes and ontology arguments. Reports remain RDFLib
graphs. PyOxigraph is optional; install this source tree with `uv sync --locked --extra oxigraph --extra test`,
or install the built wheel with its `oxigraph` extra. The tested
version is PyOxigraph 0.5.11. Runtime inference does not require owlrl.

Named graphs remain available to SPARQL `GRAPH`; Core constraints use their
union. Store blank-node labels remain connected to the corresponding focus/value
nodes in the report. Values already canonicalized by the Store cannot recover
their earlier lexical spellings.
Store strings are exposed as explicit xsd:string, matching pySHACL's Store
adapter. A plain string in an RDFLib shapes graph remains a different RDF term
for constraints such as `sh:hasValue`.

By default the caller's Store is unchanged. `inplace=True` commits new rule and
inference quads after successful execution, atomically. Existing quads are not
replayed, so unrelated concurrent deletions are not undone. This is validation
of a snapshot followed by an additions transaction, not a serializable
transaction covering other writers' entire validation interval. Execution errors
commit nothing. A successful nonconforming validation may commit rule additions,
as with the existing RDFLib API.
Inference additions use the named graph `urn:pyshacl:inference`; rule additions
continue to use the default graph. Source graphs remain in their original contexts.

The Python extensions exchange native N-Quads without materializing an RDFLib
data graph. This still copies and parses a snapshot. Store inputs used for shapes
or ontology metadata are adapted through RDFLib at the boundary. There is no
shared-pointer or zero-copy contract between independently built extensions.

The Rust crate exposes `CompiledShapes::validate_store(&Store, Options, inplace)`
and `expand_store`. Those copy a consistent quad snapshot without RDF text.
They preserve contexts and use an atomic additions transaction on success.
`CompiledShapes::validate` also accepts an exact-term `oxrdf::Dataset` directly.
All native execution remains synchronous and Python calls release the GIL.

Verified by the Store regressions, native Store integration test, and an installed
abi3 wheel on Python 3.11 with no pySHACL or owlrl packages present. The full
performance matrix compares existing Store and RDFLib inputs, including their
transfer and report construction costs; see
[performance](../benchmarks/current.md).
