# Performance comparison

This measured checkpoint predates ADR 0012's recursion and undefined-function
changes. The raw artifact retains the exact source hashes used for this run.

Measured 2026-10-10T17:40:15.356346+00:00; macOS-27.0.1-arm64-arm-64bit-Mach-O; Python 3.13.16.

Warm median milliseconds. RDFLib graph input and complete RDFLib report output; Turbo includes compilation and all conversions. Reused shapes exclude compilation but still include inference. Process startup, fixture construction and file I/O are excluded. Every timed workload first passed complete report-graph isomorphism against pySHACL. These are synthetic cases, not the private workload in the screenshot.

5 interleaved samples per configuration; raw samples and source hashes are in [current.json](current.json). A larger speedup is better. Measurements are descriptive, not a confidence interval.

| Workload | Data triples | Shape triples | Results | pySHACL ms | Turbo ms | Reused ms | Speedup | Reused speedup |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| core-100-nodes-1-shapes | 290 | 10 | 10 | 3.88 | 3.17 | 2.78 | 1.23× | 1.40× |
| core-1000-nodes-1-shapes | 2,900 | 10 | 100 | 47.37 | 36.36 | 32.57 | 1.30× | 1.45× |
| core-10000-nodes-1-shapes | 29,000 | 10 | 1,000 | 643.47 | 447.67 | 675.05 | 1.44× | 0.95× |
| shapes-1000-nodes-10-shapes | 2,900 | 82 | 1 | 3.09 | 21.42 | 44.03 | 0.14× | 0.07× |
| shapes-1000-nodes-100-shapes | 2,900 | 802 | 10 | 8.95 | 45.14 | 14.86 | 0.20× | 0.60× |
| shapes-1000-nodes-1000-shapes | 2,900 | 8,002 | 100 | 157.82 | 174.68 | 46.25 | 0.90× | 3.41× |
| rules-100-nodes-1-shapes | 290 | 22 | 10 | 211.91 | 4.71 | 4.20 | 45.00× | 50.46× |
| rules-1000-nodes-1-shapes | 2,900 | 22 | 100 | 1338.18 | 44.21 | 41.09 | 30.27× | 32.57× |
| rules-5000-nodes-1-shapes | 14,500 | 22 | 500 | 10528.55 | 590.87 | 612.58 | 17.82× | 17.19× |
| rdfs-100-nodes-1-shapes | 292 | 10 | 10 | 35.60 | 15.93 | 15.41 | 2.24× | 2.31× |
| rdfs-1000-nodes-1-shapes | 2,902 | 10 | 100 | 402.24 | 186.86 | 167.60 | 2.15× | 2.40× |
| owlrl-100-nodes-1-shapes | 291 | 10 | 10 | 172.48 | 103.44 | 20.13 | 1.67× | 8.57× |
| owlrl-1000-nodes-1-shapes | 2,901 | 10 | 100 | 716.01 | 165.85 | 163.70 | 4.32× | 4.37× |

## Existing PyOxigraph Store input

Both engines receive an already loaded Store. Initial Store loading is excluded; the Python-to-Rust handoff, validation and RDFLib report construction are included. Turbo's handoff uses native N-Quads serialization and parsing; it avoids an intermediate RDFLib data graph but is not zero-copy.

| Workload | pySHACL ms | Turbo ms | Turbo reused ms | Store-to-store speedup |
|---|---:|---:|---:|---:|
| core-100-nodes-1-shapes | 7.14 | 2.28 | 2.19 | 3.13× |
| core-1000-nodes-1-shapes | 416.69 | 23.04 | 19.27 | 18.09× |
| core-10000-nodes-1-shapes | 43828.95 | 226.00 | 357.40 | 193.93× |
| shapes-1000-nodes-10-shapes | 3.66 | 8.05 | 7.33 | 0.45× |
| shapes-1000-nodes-100-shapes | 64.46 | 37.05 | 7.04 | 1.74× |
| shapes-1000-nodes-1000-shapes | 521.10 | 158.11 | 29.21 | 3.30× |
| rules-100-nodes-1-shapes | 29.32 | 3.74 | 3.33 | 7.85× |
| rules-1000-nodes-1-shapes | 721.35 | 34.97 | 43.34 | 20.62× |
| rules-5000-nodes-1-shapes | 16754.19 | 328.31 | 453.34 | 51.03× |
| rdfs-100-nodes-1-shapes | — | 8.16 | 7.86 | — |
| rdfs-1000-nodes-1-shapes | — | 95.02 | 89.48 | — |
| owlrl-100-nodes-1-shapes | — | 12.52 | 11.67 | — |
| owlrl-1000-nodes-1-shapes | — | 90.54 | 88.91 | — |

A dash means pySHACL's Store reasoning failed on a literal subject; the exact exception is recorded in JSON. No speedup is assigned to an unavailable backend.

## Loading, compilation and reasoning

Independent phase timings are diagnostic and must not be summed into the end-to-end figures. Reference loading uses RDFLib's Turtle parser. Turbo loading includes its Rust parser and conversion to RDFLib. Inference timings include a fresh copy of the data.

### core-100-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 6.97 |
| turbo_load_data | 5.23 |
| pyshacl_load_shapes | 0.44 |
| turbo_load_shapes | 0.39 |
| turbo_compile_shapes | 0.28 |
| oxigraph_store_handoff | 0.10 |

### core-1000-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 56.43 |
| turbo_load_data | 54.73 |
| pyshacl_load_shapes | 0.53 |
| turbo_load_shapes | 0.96 |
| turbo_compile_shapes | 0.27 |
| oxigraph_store_handoff | 0.79 |

### core-10000-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 647.32 |
| turbo_load_data | 627.27 |
| pyshacl_load_shapes | 0.54 |
| turbo_load_shapes | 0.52 |
| turbo_compile_shapes | 0.29 |
| oxigraph_store_handoff | 8.91 |

### shapes-1000-nodes-10-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 42.20 |
| turbo_load_data | 77.16 |
| pyshacl_load_shapes | 1.53 |
| turbo_load_shapes | 1.43 |
| turbo_compile_shapes | 1.11 |
| oxigraph_store_handoff | 0.86 |

### shapes-1000-nodes-100-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 82.56 |
| turbo_load_data | 73.30 |
| pyshacl_load_shapes | 50.72 |
| turbo_load_shapes | 19.93 |
| turbo_compile_shapes | 9.09 |
| oxigraph_store_handoff | 0.84 |

### shapes-1000-nodes-1000-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 39.62 |
| turbo_load_data | 45.48 |
| pyshacl_load_shapes | 112.40 |
| turbo_load_shapes | 108.60 |
| turbo_compile_shapes | 94.26 |
| oxigraph_store_handoff | 0.83 |

### rules-100-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 4.60 |
| turbo_load_data | 4.97 |
| pyshacl_load_shapes | 0.68 |
| turbo_load_shapes | 0.69 |
| turbo_compile_shapes | 0.43 |
| oxigraph_store_handoff | 0.11 |

### rules-1000-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 79.07 |
| turbo_load_data | 100.37 |
| pyshacl_load_shapes | 0.65 |
| turbo_load_shapes | 0.60 |
| turbo_compile_shapes | 0.38 |
| oxigraph_store_handoff | 0.79 |

### rules-5000-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 247.88 |
| turbo_load_data | 391.14 |
| pyshacl_load_shapes | 0.71 |
| turbo_load_shapes | 0.55 |
| turbo_compile_shapes | 0.42 |
| oxigraph_store_handoff | 4.08 |

### rdfs-100-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 4.24 |
| turbo_load_data | 4.62 |
| pyshacl_load_shapes | 0.46 |
| turbo_load_shapes | 0.43 |
| turbo_compile_shapes | 0.26 |
| oxigraph_store_handoff | 0.11 |
| pyshacl_reasoning_including_copy | 30.33 |
| turbo_reasoning_including_copy_and_conversion | 11.96 |
| pyshacl_validation_after_reasoning | 3.98 |
| turbo_validation_after_reasoning_reused_shapes | 3.93 |

Inferred graphs: pySHACL 598 triples; Turbo 507. Entire inferred graphs isomorphic: **False**.
Generalized triples (literal subjects or non-IRI predicates): pySHACL 91; Turbo 0. Ordinary RDF portions isomorphic: **True**. This diagnostic does not replace the full-graph comparison.
Validation reports agree for this workload, but the complete inferred graphs differ. This row does **not** establish equivalent reasoning coverage or a like-for-like reasoner speedup.

### rdfs-1000-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 40.84 |
| turbo_load_data | 47.31 |
| pyshacl_load_shapes | 0.46 |
| turbo_load_shapes | 0.45 |
| turbo_compile_shapes | 0.31 |
| oxigraph_store_handoff | 0.83 |
| pyshacl_reasoning_including_copy | 313.08 |
| turbo_reasoning_including_copy_and_conversion | 134.23 |
| pyshacl_validation_after_reasoning | 37.24 |
| turbo_validation_after_reasoning_reused_shapes | 39.30 |

Inferred graphs: pySHACL 5,818 triples; Turbo 4,917. Entire inferred graphs isomorphic: **False**.
Generalized triples (literal subjects or non-IRI predicates): pySHACL 901; Turbo 0. Ordinary RDF portions isomorphic: **True**. This diagnostic does not replace the full-graph comparison.
Validation reports agree for this workload, but the complete inferred graphs differ. This row does **not** establish equivalent reasoning coverage or a like-for-like reasoner speedup.

### owlrl-100-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 4.35 |
| turbo_load_data | 4.79 |
| pyshacl_load_shapes | 0.53 |
| turbo_load_shapes | 0.49 |
| turbo_compile_shapes | 0.26 |
| oxigraph_store_handoff | 0.11 |
| pyshacl_reasoning_including_copy | 160.72 |
| turbo_reasoning_including_copy_and_conversion | 26.19 |
| pyshacl_validation_after_reasoning | 10.25 |
| turbo_validation_after_reasoning_reused_shapes | 4.44 |

Inferred graphs: pySHACL 696 triples; Turbo 604. Entire inferred graphs isomorphic: **False**.
Generalized triples (literal subjects or non-IRI predicates): pySHACL 92; Turbo 0. Ordinary RDF portions isomorphic: **True**. This diagnostic does not replace the full-graph comparison.
Validation reports agree for this workload, but the complete inferred graphs differ. This row does **not** establish equivalent reasoning coverage or a like-for-like reasoner speedup.

### owlrl-1000-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 40.94 |
| turbo_load_data | 42.95 |
| pyshacl_load_shapes | 0.48 |
| turbo_load_shapes | 0.43 |
| turbo_compile_shapes | 0.25 |
| oxigraph_store_handoff | 0.81 |
| pyshacl_reasoning_including_copy | 586.63 |
| turbo_reasoning_including_copy_and_conversion | 125.26 |
| pyshacl_validation_after_reasoning | 36.97 |
| turbo_validation_after_reasoning_reused_shapes | 35.22 |

Inferred graphs: pySHACL 5,916 triples; Turbo 5,014. Entire inferred graphs isomorphic: **False**.
Generalized triples (literal subjects or non-IRI predicates): pySHACL 902; Turbo 0. Ordinary RDF portions isomorphic: **True**. This diagnostic does not replace the full-graph comparison.
Validation reports agree for this workload, but the complete inferred graphs differ. This row does **not** establish equivalent reasoning coverage or a like-for-like reasoner speedup.

Compatibility remains incomplete; this benchmark only certifies the displayed workloads. Native OWL-RL coverage is still being expanded. No result here establishes 100% pySHACL compatibility.

## Shared machine load

Other workspace Rust builds ran during measurement. A captured load average was 53.7 with eight concurrent compiler processes; see [load observation](current-load.json). Samples show substantial scheduling variation, including some reused-shape medians slower than fresh compilation. Treat these figures as descriptive measurements under load, not stable speedup guarantees. Every recorded application and dependency source hash was verified unchanged after the run.
