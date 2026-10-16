# ADR 0029: Transfer RDFLib execution data as typed term batches

Status: Accepted

RDFLib data previously crossed the Python/Rust boundary as serialized RDF, then
native reports and expanded graphs were serialized and parsed again in Python.
This repeats parsing and formatting even though both sides already have terms.

Use a table of unique term records and indexed quads for RDFLib validation and
rule execution. Records distinguish IRIs, blank nodes, plain literals, explicitly
typed literals and language-tagged literals. Preserve lexical forms without
normalization. Default graph names are represented separately from named IRIs or
blank nodes. Validate term kinds, positions and indices at the native boundary.

Return typed batches on this execution path and construct RDFLib terms directly.
Keep document and Store text adapters, which have their own parsing and Store
datatype contracts. Shape loading/compilation and other existing textual APIs
retain their current boundary. Public validation and rule signatures stay the
same. Internal Input snapshots can carry either representation and retain its
format when updated.

Regressions block Graph serialization and N-Triples parsing during execution,
cover Graph/Dataset validation and rules, exact datatype/lexical forms, named
blank-node contexts, blank-node mapping, internal snapshots and malformed batches.
Synthetic Graph benchmarks retained beside the driver show 7.67 to 4.94 ms for
validation and 35.46 to 17.53 ms for complete rule output on 1,800 input triples.
These are local workload measurements, not general speedup claims.
