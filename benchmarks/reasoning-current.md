# Performance comparison

Measured 2026-10-10T16:57:00.428576+00:00; macOS-27.0.1-arm64-arm-64bit-Mach-O; Python 3.13.16.

Warm median milliseconds. RDFLib graph input and complete RDFLib report output; Turbo includes compilation and all conversions. Reused shapes exclude compilation but still include inference. Process startup, fixture construction and file I/O are excluded. Every timed workload first passed complete report-graph isomorphism against pySHACL. These are synthetic cases.

5 interleaved samples per configuration; raw samples and source hashes are in [reasoning-current.json](reasoning-current.json). A larger speedup is better. Measurements are descriptive, not a confidence interval.

| Workload | Data triples | Shape triples | Results | pySHACL ms | Turbo ms | Reused ms | Speedup | Reused speedup |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| rdfs-100-nodes-1-shapes | 292 | 10 | 10 | 33.51 | 15.38 | 15.25 | 2.18× | 2.20× |
| rdfs-1000-nodes-1-shapes | 2,902 | 10 | 100 | 340.37 | 155.19 | 146.45 | 2.19× | 2.32× |
| owlrl-100-nodes-1-shapes | 291 | 10 | 10 | 69.55 | 20.42 | 19.96 | 3.41× | 3.48× |
| owlrl-1000-nodes-1-shapes | 2,901 | 10 | 100 | 622.26 | 163.00 | 168.15 | 3.82× | 3.70× |

## Existing PyOxigraph Store input

Both engines receive an already loaded Store. Initial Store loading is excluded; the Python-to-Rust handoff, validation and RDFLib report construction are included. Turbo's handoff uses native N-Quads serialization and parsing; it avoids an intermediate RDFLib data graph but is not zero-copy.

| Workload | pySHACL ms | Turbo ms | Turbo reused ms | Store-to-store speedup |
|---|---:|---:|---:|---:|
| rdfs-100-nodes-1-shapes | — | 6.67 | 6.27 | — |
| rdfs-1000-nodes-1-shapes | — | 59.90 | 60.15 | — |
| owlrl-100-nodes-1-shapes | — | 10.36 | 9.66 | — |
| owlrl-1000-nodes-1-shapes | — | 71.44 | 70.02 | — |

A dash means pySHACL's Store reasoning failed on a literal subject; the exact exception is recorded in JSON. No speedup is assigned to an unavailable backend.

## Loading, compilation and reasoning

Independent phase timings are diagnostic and must not be summed into the end-to-end figures. Reference loading uses RDFLib's Turtle parser. Turbo loading includes its Rust parser and conversion to RDFLib. Inference timings include a fresh copy of the data.

### rdfs-100-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 4.26 |
| turbo_load_data | 4.37 |
| pyshacl_load_shapes | 0.49 |
| turbo_load_shapes | 0.35 |
| turbo_compile_shapes | 0.25 |
| oxigraph_store_handoff | 0.10 |
| pyshacl_reasoning_including_copy | 29.47 |
| turbo_reasoning_including_copy_and_conversion | 11.54 |
| pyshacl_validation_after_reasoning | 4.02 |
| turbo_validation_after_reasoning_reused_shapes | 3.78 |

Inferred graphs: pySHACL 598 triples; Turbo 507. Entire inferred graphs isomorphic: **False**.
Generalized triples (literal subjects or non-IRI predicates): pySHACL 91; Turbo 0. Ordinary RDF portions isomorphic: **True**. This diagnostic does not replace the full-graph comparison.
Validation reports agree for this workload, but the complete inferred graphs differ. This row does **not** establish equivalent reasoning coverage or a like-for-like reasoner speedup.

### rdfs-1000-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 40.75 |
| turbo_load_data | 42.93 |
| pyshacl_load_shapes | 0.47 |
| turbo_load_shapes | 0.46 |
| turbo_compile_shapes | 0.27 |
| oxigraph_store_handoff | 0.83 |
| pyshacl_reasoning_including_copy | 300.43 |
| turbo_reasoning_including_copy_and_conversion | 111.81 |
| pyshacl_validation_after_reasoning | 37.91 |
| turbo_validation_after_reasoning_reused_shapes | 37.69 |

Inferred graphs: pySHACL 5,818 triples; Turbo 4,917. Entire inferred graphs isomorphic: **False**.
Generalized triples (literal subjects or non-IRI predicates): pySHACL 901; Turbo 0. Ordinary RDF portions isomorphic: **True**. This diagnostic does not replace the full-graph comparison.
Validation reports agree for this workload, but the complete inferred graphs differ. This row does **not** establish equivalent reasoning coverage or a like-for-like reasoner speedup.

### owlrl-100-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 4.17 |
| turbo_load_data | 4.50 |
| pyshacl_load_shapes | 0.49 |
| turbo_load_shapes | 0.38 |
| turbo_compile_shapes | 0.26 |
| oxigraph_store_handoff | 0.11 |
| pyshacl_reasoning_including_copy | 66.68 |
| turbo_reasoning_including_copy_and_conversion | 16.27 |
| pyshacl_validation_after_reasoning | 3.96 |
| turbo_validation_after_reasoning_reused_shapes | 4.09 |

Inferred graphs: pySHACL 696 triples; Turbo 606. Entire inferred graphs isomorphic: **False**.
Generalized triples (literal subjects or non-IRI predicates): pySHACL 92; Turbo 0. Ordinary RDF portions isomorphic: **False**. This diagnostic does not replace the full-graph comparison.
Validation reports agree for this workload, but the complete inferred graphs differ. This row does **not** establish equivalent reasoning coverage or a like-for-like reasoner speedup.

### owlrl-1000-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 42.57 |
| turbo_load_data | 43.52 |
| pyshacl_load_shapes | 0.51 |
| turbo_load_shapes | 0.46 |
| turbo_compile_shapes | 0.29 |
| oxigraph_store_handoff | 0.81 |
| pyshacl_reasoning_including_copy | 594.47 |
| turbo_reasoning_including_copy_and_conversion | 135.09 |
| pyshacl_validation_after_reasoning | 38.46 |
| turbo_validation_after_reasoning_reused_shapes | 36.94 |

Inferred graphs: pySHACL 5,916 triples; Turbo 5,016. Entire inferred graphs isomorphic: **False**.
Generalized triples (literal subjects or non-IRI predicates): pySHACL 902; Turbo 0. Ordinary RDF portions isomorphic: **False**. This diagnostic does not replace the full-graph comparison.
Validation reports agree for this workload, but the complete inferred graphs differ. This row does **not** establish equivalent reasoning coverage or a like-for-like reasoner speedup.

Compatibility remains incomplete; this benchmark only certifies the displayed workloads. Native OWL-RL coverage is still being expanded. No result here establishes 100% pySHACL compatibility.
