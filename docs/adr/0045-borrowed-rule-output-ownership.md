# ADR 0045: Validate borrowed rule outputs before acceptance

Status: Accepted

The borrowed adapter owns rule staging and commits only after its caller accepts
the yielded result. Validate output ownership inside that context, before warning
delivery and before the adapter resumes its acceptance path. An invalid result
raises while the adapter can still abort its transaction.

Normalize native DataGraph wrappers to their selected native view. In-place
execution must yield that exact source object. Independent execution preserves
the Graph, Dataset or Store category, selected Graph identifier, and owns a
different native backend object. Transaction independent output is a Store.
Subclasses remain supported; retired raw NativeDataset results are not the
borrowed public protocol. No transport or fallback repairs invalid outputs.
