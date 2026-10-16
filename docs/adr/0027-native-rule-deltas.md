# ADR 0027: Retain rule additions at insertion time

Status: Accepted

Computing additions from serialized before/after graphs repeated native parsing
and serialized the entire expanded dataset. The rule executor already knows
which insertions are new.

Expose `expand_rules_delta` and optionally record successful insertions in a
separate exact-term dataset. Rules retain their original visibility and ordering;
the delta accumulates across rules and iterations. Named-graph union inputs do
not leak synthetic union statements into the delta. Python inplace RDFLib rule
calls serialize and decode only this delta, committing after successful native
execution. Other callers retain complete expanded output.

Do not infer deltas from triple counts or normalize RDF terms. Existing triples,
including a triple already present in the union, are excluded. Tests cover
noncanonical numeric literals, named contexts, repeated expansion, discarded
output avoidance and bypassing the serialized before/after comparison.
