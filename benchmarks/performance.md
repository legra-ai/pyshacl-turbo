# Performance comparison

Measured 2026-10-10T16:27:02.795433+00:00; macOS-27.0.1-arm64-arm-64bit-Mach-O; Python 3.13.16.

Warm median milliseconds. RDFLib graph input and complete RDFLib report output; Turbo includes compilation and all conversions. Reused shapes exclude compilation but still include inference. Process startup, fixture construction and file I/O are excluded. Every timed workload first passed complete report-graph isomorphism against pySHACL. These are synthetic cases, not the private workload in the screenshot.

5 interleaved samples per configuration; raw samples and source hashes are in [performance.json](performance.json). A larger speedup is better. Measurements are descriptive, not a confidence interval.

| Workload | Data triples | Shape triples | Results | pySHACL ms | Turbo ms | Reused ms | Speedup | Reused speedup |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| core-100-nodes-1-shapes | 290 | 10 | 10 | 3.67 | 2.81 | 2.63 | 1.30× | 1.39× |
| core-1000-nodes-1-shapes | 2,900 | 10 | 100 | 34.77 | 24.88 | 24.39 | 1.40× | 1.43× |
| core-10000-nodes-1-shapes | 29,000 | 10 | 1,000 | 352.84 | 384.02 | 305.66 | 0.92× | 1.15× |
| shapes-1000-nodes-10-shapes | 2,900 | 82 | 1 | 1.26 | 14.20 | 13.07 | 0.09× | 0.10× |
| shapes-1000-nodes-100-shapes | 2,900 | 802 | 10 | 8.77 | 24.83 | 14.14 | 0.35× | 0.62× |
| shapes-1000-nodes-1000-shapes | 2,900 | 8,002 | 100 | 130.32 | 134.23 | 27.56 | 0.97× | 4.73× |
| rules-100-nodes-1-shapes | 290 | 22 | 10 | 136.95 | 5.14 | 4.38 | 26.67× | 31.23× |
| rules-1000-nodes-1-shapes | 2,900 | 22 | 100 | 1379.76 | 41.33 | 40.57 | 33.38× | 34.01× |
| rules-5000-nodes-1-shapes | 14,500 | 22 | 500 | 5878.28 | 221.44 | 234.04 | 26.55× | 25.12× |
| rdfs-100-nodes-1-shapes | 292 | 10 | 10 | 33.43 | 16.66 | 15.87 | 2.01× | 2.11× |
| rdfs-1000-nodes-1-shapes | 2,902 | 10 | 100 | 345.87 | 156.36 | 157.68 | 2.21× | 2.19× |
| owlrl-100-nodes-1-shapes | 291 | 10 | 10 | 67.69 | 20.48 | 19.80 | 3.31× | 3.42× |
| owlrl-1000-nodes-1-shapes | 2,901 | 10 | 100 | 624.54 | 195.48 | 187.96 | 3.19× | 3.32× |

## Existing PyOxigraph Store input

Both engines receive an already loaded Store. Initial Store loading is excluded; the Python-to-Rust handoff, validation and RDFLib report construction are included. Turbo's handoff uses native N-Quads serialization and parsing; it avoids an intermediate RDFLib data graph but is not zero-copy.

| Workload | pySHACL ms | Turbo ms | Turbo reused ms | Store-to-store speedup |
|---|---:|---:|---:|---:|
| core-100-nodes-1-shapes | 6.86 | 2.13 | 2.01 | 3.22× |
| core-1000-nodes-1-shapes | 234.82 | 19.11 | 17.46 | 12.29× |
| core-10000-nodes-1-shapes | 27094.06 | 207.40 | 277.59 | 130.63× |
| shapes-1000-nodes-10-shapes | 3.53 | 6.39 | 5.25 | 0.55× |
| shapes-1000-nodes-100-shapes | 32.88 | 17.21 | 6.39 | 1.91× |
| shapes-1000-nodes-1000-shapes | 319.40 | 120.91 | 17.66 | 2.64× |
| rules-100-nodes-1-shapes | 29.48 | 3.77 | 3.22 | 7.81× |
| rules-1000-nodes-1-shapes | 566.30 | 33.76 | 34.46 | 16.78× |
| rules-5000-nodes-1-shapes | 8938.49 | 185.43 | 178.34 | 48.20× |
| rdfs-100-nodes-1-shapes | — | 7.25 | 7.09 | — |
| rdfs-1000-nodes-1-shapes | — | 67.34 | 67.03 | — |
| owlrl-100-nodes-1-shapes | — | 11.28 | 11.02 | — |
| owlrl-1000-nodes-1-shapes | — | 95.83 | 95.89 | — |

A dash means pySHACL's Store reasoning failed on a literal subject; the exact exception is recorded in JSON. No speedup is assigned to an unavailable backend.

## Loading, compilation and reasoning

Independent phase timings are diagnostic and must not be summed into the end-to-end figures. Reference loading uses RDFLib's Turtle parser. Turbo loading includes its Rust parser and conversion to RDFLib. Inference timings include a fresh copy of the data.

### core-100-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 3.89 |
| turbo_load_data | 4.08 |
| pyshacl_load_shapes | 0.31 |
| turbo_load_shapes | 0.27 |
| turbo_compile_shapes | 0.17 |
| oxigraph_store_handoff | 0.07 |

### core-1000-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 37.88 |
| turbo_load_data | 39.81 |
| pyshacl_load_shapes | 0.40 |
| turbo_load_shapes | 0.32 |
| turbo_compile_shapes | 0.21 |
| oxigraph_store_handoff | 0.72 |

### core-10000-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 541.86 |
| turbo_load_data | 557.66 |
| pyshacl_load_shapes | 0.53 |
| turbo_load_shapes | 0.46 |
| turbo_compile_shapes | 0.29 |
| oxigraph_store_handoff | 8.23 |

### shapes-1000-nodes-10-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 41.44 |
| turbo_load_data | 43.34 |
| pyshacl_load_shapes | 1.40 |
| turbo_load_shapes | 1.35 |
| turbo_compile_shapes | 1.03 |
| oxigraph_store_handoff | 0.80 |

### shapes-1000-nodes-100-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 40.65 |
| turbo_load_data | 43.40 |
| pyshacl_load_shapes | 10.69 |
| turbo_load_shapes | 10.72 |
| turbo_compile_shapes | 8.90 |
| oxigraph_store_handoff | 0.77 |

### shapes-1000-nodes-1000-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 41.04 |
| turbo_load_data | 46.60 |
| pyshacl_load_shapes | 122.44 |
| turbo_load_shapes | 109.42 |
| turbo_compile_shapes | 98.45 |
| oxigraph_store_handoff | 0.83 |

### rules-100-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 4.26 |
| turbo_load_data | 4.58 |
| pyshacl_load_shapes | 0.60 |
| turbo_load_shapes | 0.62 |
| turbo_compile_shapes | 0.39 |
| oxigraph_store_handoff | 0.10 |

### rules-1000-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 39.99 |
| turbo_load_data | 43.44 |
| pyshacl_load_shapes | 0.69 |
| turbo_load_shapes | 0.60 |
| turbo_compile_shapes | 0.43 |
| oxigraph_store_handoff | 0.73 |

### rules-5000-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 198.23 |
| turbo_load_data | 301.65 |
| pyshacl_load_shapes | 0.66 |
| turbo_load_shapes | 0.52 |
| turbo_compile_shapes | 0.39 |
| oxigraph_store_handoff | 3.86 |

### rdfs-100-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 4.37 |
| turbo_load_data | 4.57 |
| pyshacl_load_shapes | 0.40 |
| turbo_load_shapes | 0.39 |
| turbo_compile_shapes | 0.23 |
| oxigraph_store_handoff | 0.11 |
| pyshacl_reasoning_including_copy | 29.68 |
| turbo_reasoning_including_copy_and_conversion | 12.71 |
| pyshacl_validation_after_reasoning | 3.96 |
| turbo_validation_after_reasoning_reused_shapes | 3.92 |

Inferred graphs: pySHACL 598 triples; Turbo 514. Entire inferred graphs isomorphic: **False**.
Validation reports agree for this workload, but the complete inferred graphs differ. This row does **not** establish equivalent reasoning coverage or a like-for-like reasoner speedup.

### rdfs-1000-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 39.33 |
| turbo_load_data | 44.18 |
| pyshacl_load_shapes | 0.49 |
| turbo_load_shapes | 0.45 |
| turbo_compile_shapes | 0.28 |
| oxigraph_store_handoff | 0.85 |
| pyshacl_reasoning_including_copy | 303.66 |
| turbo_reasoning_including_copy_and_conversion | 119.67 |
| pyshacl_validation_after_reasoning | 36.10 |
| turbo_validation_after_reasoning_reused_shapes | 35.40 |

Inferred graphs: pySHACL 5,818 triples; Turbo 4,924. Entire inferred graphs isomorphic: **False**.
Validation reports agree for this workload, but the complete inferred graphs differ. This row does **not** establish equivalent reasoning coverage or a like-for-like reasoner speedup.

### owlrl-100-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 4.19 |
| turbo_load_data | 4.47 |
| pyshacl_load_shapes | 0.42 |
| turbo_load_shapes | 0.39 |
| turbo_compile_shapes | 0.24 |
| oxigraph_store_handoff | 0.09 |
| pyshacl_reasoning_including_copy | 65.19 |
| turbo_reasoning_including_copy_and_conversion | 16.32 |
| pyshacl_validation_after_reasoning | 3.88 |
| turbo_validation_after_reasoning_reused_shapes | 3.66 |

Inferred graphs: pySHACL 696 triples; Turbo 516. Entire inferred graphs isomorphic: **False**.
Validation reports agree for this workload, but the complete inferred graphs differ. This row does **not** establish equivalent reasoning coverage or a like-for-like reasoner speedup.

### owlrl-1000-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 41.84 |
| turbo_load_data | 53.79 |
| pyshacl_load_shapes | 0.59 |
| turbo_load_shapes | 0.47 |
| turbo_compile_shapes | 0.32 |
| oxigraph_store_handoff | 0.87 |
| pyshacl_reasoning_including_copy | 593.88 |
| turbo_reasoning_including_copy_and_conversion | 154.02 |
| pyshacl_validation_after_reasoning | 36.53 |
| turbo_validation_after_reasoning_reused_shapes | 38.86 |

Inferred graphs: pySHACL 5,916 triples; Turbo 4,926. Entire inferred graphs isomorphic: **False**.
Validation reports agree for this workload, but the complete inferred graphs differ. This row does **not** establish equivalent reasoning coverage or a like-for-like reasoner speedup.

Compatibility remains incomplete; this benchmark only certifies the displayed workloads. Native OWL-RL coverage is still being expanded. No result here establishes 100% pySHACL compatibility.

This complete matrix precedes the metadata-discovery and native inference
initialization fixes. The JSON records the measured source hashes. Updated
reasoning measurements are in [reasoning-current.md](reasoning-current.md).
The current seven-sample Core regression is recorded in [core-current.txt](core-current.txt):
1,000-node medians were 37.89 ms for pySHACL/RDFLib, 36.12 ms for Turbo/RDFLib,
and 19.58 ms for Turbo/Store. Reports matched before timing. Samples varied
substantially on this shared machine; the raw timings are retained.
