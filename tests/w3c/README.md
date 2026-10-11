# W3C test provenance and comparison

The full test tree is vendored from [w3c/data-shapes](https://github.com/w3c/data-shapes/tree/07458ebb1ece6addc664636d70b08444a7b66609/data-shapes-test-suite/tests),
commit `07458ebb1ece6addc664636d70b08444a7b66609`. Source fixtures are unmodified.
Their licenses are in `LICENSE.md` and `SOFTWARE-LICENSE.html`.

The recursive manifests contain 120 validation cases: 98 Core and 22 SPARQL.
Document inputs pass all 98 Core and 22 SPARQL cases. RDFLib Graph inputs pass
97 Core cases and all 22 SPARQL cases. Core `property/uniqueLang-002` expects
boolean lexical `1` not to activate the constraint. Turbo follows pySHACL 0.40.1:
document inputs leave it inactive, while ordinary Graph inputs treat it as true
(ADR 0007). The Graph result remains a mismatch in the coverage report and a
strict expected failure in pytest. It is not counted as a Graph conformance pass.

`suite_harness.py` resolves graph references only inside this pinned directory.
It preserves intentionally invalid literal spellings. Report comparisons retain
all results and all fields. Implementation-generated messages and optional
nested details are omitted only when the fixture does not prescribe them.
Copied descriptions of input nodes are not treated as additional result fields.
Graph-input blank-node references retain identity. Documents are parsed
independently, so their blank nodes compare by descriptions and shared
references; missing or changed descriptions and changed node sharing fail.
Result paths compare their path structure, allowing shared and separately
copied encodings of the same path.
See the [W3C report comparison contract](https://w3c.github.io/data-shapes/data-shapes-test-suite/).
Dedicated comparator tests reject missing/duplicate results and changed fields.
Differential tests separately compare complete pySHACL report graphs without
this W3C projection.

`make coverage` records every manifest case separately for both input paths,
including unsupported features, mismatches and errors. The complete downloaded
file inventory and immutable revisions are in `../suite-sources.json`. Files not included by a manifest (such
as the proposed `sparql/component/nodeValidator-001.ttl`) are vendored but are
not counted among those 120 cases.
