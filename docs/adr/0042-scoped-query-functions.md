# ADR 0042: Borrow SHACL function state for query execution

Status: Accepted

Store-backed validation must read the same active transaction as native shape
traversal, including pending inserts and removals. A transaction is thread-affine
and borrowed. Capturing a copied Dataset in a static Send + Sync callback violates
that ownership and scales memory with the complete input.

Expose execution-scoped custom functions through
`QueryableDataset::scoped_custom_function`. The callback lifetime is tied to the
borrowed query source and its lazy results. Callbacks may borrow local, non-Send
evaluation state. Explicit evaluator registrations take precedence over source
callbacks. Neither parsed/prepared queries nor cached algebra plans retain the
callbacks.
There is no global or thread-local callback context, unsafe lifetime extension,
whole-source snapshot, or callback serialized across owner threads.

The canonical engine will compose its existing GraphRead, UnionGraph,
OverlayGraph and QueryGraph views, and bind SHACL functions to that same borrowed
view. All engine implementation and vendored evaluator changes must participate
in coordinated source identity before the owning runtime adopts this API.
Provider engine pins and consumer fingerprints change together after actual
transaction and graph-scope regressions pass. Integration protocol remains 1.

The actual evaluator crate computes a compact SHA-256 at build time over sorted
Rust sources, Cargo.toml, build.rs and enabled Cargo feature selections. Directory
and file rerun declarations discover added sources. The engine incorporates the
compiled evaluator digest, not files read from a potentially unused canonical
workspace vendor path. Runtime payloads retain no raw evaluator source bytes.
Inventory regressions verify discovery and feature/source sensitivity. A provider
Cargo patch must compile the reviewed evaluator API and matching identity before
paired fingerprints agree.

Both extensions enable the same evaluator profile: undefined function expression
errors, exact custom-function terms, exact term builtins, RDF set union and cached
query plans. Share the actual evaluator source fixes, rather than declaring
matching flags over divergent code. The canonical oxrdf patch also shares the
runtime's exact blank identity and lifetime-safe indexed Dataset pattern source.
The sparopt, spargebra and oxsdatatypes sources are audited equal. Evaluator source
identity alone does not attest these dependencies: paired wheel tests verify the
effective shared RDF identity profiles, including lexical literals, explicit and
plain strings, blank identities, source graph scopes and SPARQL union bags.

Generic transaction GraphRead implementations preserve the physical backend's
exact RDF terms. RDF 1.1 string conversion belongs exclusively to the upstream
Store convenience methods, through an explicit Rdf11Transaction view that maps
both indexed filters and returned terms. It must never coerce an exact-term
owner's plain strings into explicit datatype terms: union representative lookups
must address the same term that was returned by the original read.

## Attest all compiled query and RDF dependencies

The engine identity incorporates the actual compiled source and semantic feature
digests of Oxigraph, oxrdf, oxsdatatypes, spargebra, sparopt and spareval. An
optimizer patch or RDF storage profile cannot remain invisible behind an
unchanged evaluator digest. Each crate runs the same tracked build helper over
its own sorted recursive Rust source inventory, manifest and build script. The
helper itself is an input. Stable relative names and normalized CRLF transport
make identities independent of checkout paths. New source modules are discovered
without maintaining a second list. Both source distributions and Cargo Git
checkouts must retain the helper and every crate's identity implementation.

Canonical and owning-runtime builds use the same reviewed dependency source and
exact-term-storage semantic profile. The canonical Store convenience methods
retain their explicit RDF 1.1 view; exact borrowed owners retain original terms.
Every enabled feature contributes to semantic identity except Oxigraph's three
audited persistence capabilities: rocksdb, rocksdb-debug and rocksdb-pkg-config.
These contribute to a separately exported backend capability digest. They select
the persistence implementation without changing the borrowed GraphRead query/RDF
contract. No additional feature is excluded by default. Capability identity does
not claim to attest the external RocksDB implementation. Memory/persistent owner
controls must verify the same borrowed semantics; canonical validation does not
link an otherwise unused persistence backend to match capability flags.
