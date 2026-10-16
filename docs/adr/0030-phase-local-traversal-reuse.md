# ADR 0030: Reuse graph traversals within a stable execution phase

Status: Accepted

Repeated shapes and rule conditions can traverse the same complex property path,
test the same node/class membership or discover the same class targets while
reading identical data. Query-plan preparation does not remove this graph work.

Keep these results in the execution's Evaluation context. Complex path keys use
the structural path and focus term; membership keys use value and required class;
class-target keys use the required class. Preserve original traversal ordering,
cycle handling and errors. Simple predicate paths continue to use the indexed
lookup directly. Do not cache recursive shape-validation results or SPARQL target
results.

Clear all traversal results after any rule commits additions. Subsequent rules
and iterations then discover fresh paths, types and subclass targets. Validation
starts a separate execution context after rule expansion, and the next invocation
starts fresh. Results never live in the compiled program or an implicit mutable
graph cache.

Retain at most 1,024 entries and 32,768 result terms. Clear the window when its
budget fills and do not retain an individually oversized result. Eviction changes
reuse only, not graph observations. Native work-count and budget tests cover
reuse and phase refresh. Python regressions cover path/class rule conditions
and targets activated by new type/subclass statements.

The retained synthetic benchmark supplies serialized input outside the timer to
isolate native traversal work from term-transfer changes. Twenty-four shapes
sharing a 300-edge transitive path changed from 15.12 to 1.28 ms median. A single
predicate-path workload was effectively unchanged (1.96 versus 1.90 ms). These
measurements describe the local fixtures, not general validation speedups.
