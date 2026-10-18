
## Borrowed SPARQL graph architecture

[`GraphRead`] is the storage boundary: it streams indexed quad matches, enumerates
named graphs and checks graph existence. Implementations for an in-memory
`oxigraph::model::Dataset` and an open `oxigraph::store::Transaction` preserve
their graph contexts. Transaction reads include pending insertions and deletions.

[`UnionGraph`] optionally exposes distinct data triples in the default graph while
preserving named contexts. [`OverlayGraph`] optionally adds a borrowed shapes
union under a fresh named graph, including when shapes are empty. For SHACL, wrap
the data union in the shapes overlay, in that order. Shapes stay outside the data
union and remain available to queries through the reserved shapes graph name.

[`QueryGraph`] implements `spareval::QueryableDataset` for these borrowed sources.
The existing SPARQL evaluator retains parsing, planning, joins, expressions and
property paths. The adapter translates graph matching: an absent [`GraphRead`]
graph filter includes all contexts, whereas a SPARQL wildcard graph pattern
matches named graphs only. Named-graph metadata retains empty native and overlay
graphs. Invalid subject, predicate or graph term kinds yield no matches.

A source must stay consistent while results are consumed. Rust lifetimes retain
its borrow; temporary match terms need not outlive the returned stream. Read and
metadata errors remain errors, including during lazy query-result iteration.
The adapter preserves stored RDF terms; it cannot restore lexical forms already
normalized by a backend.

The adapter and views do not copy the base dataset or collect all graph names.
The evaluator's query-dependent joins, sorting, aggregates and output can still
consume memory. Transaction ownership and commit/rollback remain with the caller.

**Integration status:** these are public Rust building blocks. Complete
transaction-backed SHACL validation and snapshot-free SHACL function callbacks
still require adoption. Existing `validate_store` and `expand_store` APIs continue
to use consistent dataset snapshots.

### Query pending changes through the composed views

```rust
use pyshacl_turbo_engine::{OverlayGraph, QueryGraph, UnionGraph};
use pyshacl_turbo_engine::oxigraph::{
    model::{Dataset, NamedNode, Quad},
    sparql::{QueryResults, SparqlEvaluator},
    store::Store,
};

let store = Store::new()?;
let mut transaction = store.start_transaction()?;
transaction.insert(&Quad::new(
    NamedNode::new("urn:alice")?,
    NamedNode::new("urn:knows")?,
    NamedNode::new("urn:bob")?,
    NamedNode::new("urn:data")?,
));

{
    let shapes = Dataset::new();
    let data_union = UnionGraph::new(&transaction);
    let view = OverlayGraph::new(
        &data_union, &shapes, NamedNode::new("urn:shapes")?.into(),
    )?;
    let result = SparqlEvaluator::new()
        .parse_query("ASK { <urn:alice> <urn:knows> <urn:bob> }")?
        .on_queryable_dataset(QueryGraph::new(&view))
        .execute()?;
    assert!(matches!(result, QueryResults::Boolean(true)));
}

// Dropping the transaction aborts its pending changes.
drop(transaction);
assert!(store.is_empty()?);
# Ok::<(), Box<dyn std::error::Error>>(())
```
