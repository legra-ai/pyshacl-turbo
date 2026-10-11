# Performance comparison

Measured 2026-10-11T17:32:08.791027+00:00; macOS-27.0.1-arm64-arm-64bit-Mach-O; Python 3.13.16.

Warm median milliseconds. RDFLib graph input and complete RDFLib report output; Turbo includes compilation and all conversions. Reused shapes exclude compilation but still include inference. Process startup, fixture construction and file I/O are excluded. Every timed workload first passed complete report-graph isomorphism against pySHACL. These are synthetic cases, not the private workload in the screenshot.

5 interleaved samples per configuration; raw samples and source hashes are in [drop-in.json](drop-in.json). A larger speedup is better. Measurements are descriptive, not a confidence interval.

Load note: Release build from the working tree with the public-contract fixes; see source hashes. This task ran no concurrent builds or tests during the matrix. Other workspace Rust compilation was observed, so these are descriptive local measurements under background activity, not isolated-machine capacity estimates.

| Workload | Data triples | Shape triples | Results | pySHACL ms | Turbo ms | Reused ms | Speedup | Reused speedup |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| core-100-nodes-1-shapes | 290 | 10 | 10 | 3.77 | 3.05 | 2.64 | 1.24× | 1.43× |
| core-1000-nodes-1-shapes | 2,900 | 10 | 100 | 36.86 | 26.34 | 25.65 | 1.40× | 1.44× |
| core-10000-nodes-1-shapes | 29,000 | 10 | 1,000 | 385.03 | 418.68 | 337.25 | 0.92× | 1.14× |
| sparql-patterns-100-nodes-1-shapes | 300 | 7 | 10 | 622.14 | 5.05 | 4.78 | 123.08× | 130.04× |
| sparql-patterns-1000-nodes-1-shapes | 3,000 | 7 | 100 | 6023.02 | 47.98 | 45.40 | 125.54× | 132.66× |
| shapes-1000-nodes-10-shapes | 2,900 | 82 | 1 | 1.12 | 14.31 | 12.96 | 0.08× | 0.09× |
| shapes-1000-nodes-100-shapes | 2,900 | 802 | 10 | 8.86 | 24.32 | 14.14 | 0.36× | 0.63× |
| shapes-1000-nodes-1000-shapes | 2,900 | 8,002 | 100 | 88.27 | 134.52 | 24.43 | 0.66× | 3.61× |
| rules-100-nodes-1-shapes | 290 | 22 | 10 | 120.45 | 4.46 | 3.97 | 27.01× | 30.34× |
| rules-1000-nodes-1-shapes | 2,900 | 22 | 100 | 1247.07 | 40.81 | 40.01 | 30.56× | 31.17× |
| rules-5000-nodes-1-shapes | 14,500 | 22 | 500 | 6291.95 | 220.28 | 231.79 | 28.56× | 27.14× |

## Existing PyOxigraph Store input

Both engines receive an already loaded Store. Initial Store loading is excluded; the Python-to-Rust handoff, validation and RDFLib report construction are included. Turbo's handoff uses native N-Quads serialization and parsing; it avoids an intermediate RDFLib data graph but is not zero-copy.

| Workload | pySHACL ms | Turbo ms | Turbo reused ms | Store-to-store speedup |
|---|---:|---:|---:|---:|
| core-100-nodes-1-shapes | 7.25 | 2.37 | 1.94 | 3.06× |
| core-1000-nodes-1-shapes | 255.79 | 20.64 | 18.93 | 12.39× |
| core-10000-nodes-1-shapes | 29939.42 | 231.02 | 229.67 | 129.59× |
| sparql-patterns-100-nodes-1-shapes | 17.10 | 4.22 | 3.68 | 4.05× |
| sparql-patterns-1000-nodes-1-shapes | 458.14 | 36.08 | 36.35 | 12.70× |
| shapes-1000-nodes-10-shapes | 3.46 | 6.72 | 5.62 | 0.51× |
| shapes-1000-nodes-100-shapes | 30.96 | 17.40 | 6.81 | 1.78× |
| shapes-1000-nodes-1000-shapes | 311.19 | 125.86 | 16.89 | 2.47× |
| rules-100-nodes-1-shapes | 27.42 | 3.57 | 3.19 | 7.67× |
| rules-1000-nodes-1-shapes | 552.28 | 32.84 | 32.46 | 16.82× |
| rules-5000-nodes-1-shapes | 9514.75 | 194.59 | 179.72 | 48.90× |

A dash means pySHACL's Store reasoning failed on a literal subject; the exact exception is recorded in JSON. No speedup is assigned to an unavailable backend.

## Loading, compilation and reasoning

Independent phase timings are diagnostic and must not be summed into the end-to-end figures. Reference loading uses RDFLib's Turtle parser. Turbo loading includes its Rust parser and conversion to RDFLib. Inference timings include a fresh copy of the data.

### core-100-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 4.25 |
| turbo_load_data | 4.26 |
| pyshacl_load_shapes | 0.39 |
| turbo_load_shapes | 0.32 |
| turbo_compile_shapes | 0.25 |
| oxigraph_store_handoff | 0.09 |

### core-1000-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 40.58 |
| turbo_load_data | 43.08 |
| pyshacl_load_shapes | 0.46 |
| turbo_load_shapes | 0.34 |
| turbo_compile_shapes | 0.27 |
| oxigraph_store_handoff | 0.76 |

### core-10000-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 550.62 |
| turbo_load_data | 570.98 |
| pyshacl_load_shapes | 0.47 |
| turbo_load_shapes | 0.42 |
| turbo_compile_shapes | 0.29 |
| oxigraph_store_handoff | 9.31 |

### sparql-patterns-100-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 4.53 |
| turbo_load_data | 4.73 |
| pyshacl_load_shapes | 0.33 |
| turbo_load_shapes | 0.28 |
| turbo_compile_shapes | 0.24 |
| oxigraph_store_handoff | 0.10 |

### sparql-patterns-1000-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 46.46 |
| turbo_load_data | 48.99 |
| pyshacl_load_shapes | 0.41 |
| turbo_load_shapes | 0.37 |
| turbo_compile_shapes | 0.25 |
| oxigraph_store_handoff | 0.81 |

### shapes-1000-nodes-10-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 40.75 |
| turbo_load_data | 44.36 |
| pyshacl_load_shapes | 1.44 |
| turbo_load_shapes | 1.37 |
| turbo_compile_shapes | 1.16 |
| oxigraph_store_handoff | 0.79 |

### shapes-1000-nodes-100-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 41.02 |
| turbo_load_data | 43.54 |
| pyshacl_load_shapes | 10.99 |
| turbo_load_shapes | 10.55 |
| turbo_compile_shapes | 9.80 |
| oxigraph_store_handoff | 0.79 |

### shapes-1000-nodes-1000-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 40.02 |
| turbo_load_data | 46.56 |
| pyshacl_load_shapes | 113.40 |
| turbo_load_shapes | 107.46 |
| turbo_compile_shapes | 102.53 |
| oxigraph_store_handoff | 0.80 |

### rules-100-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 4.04 |
| turbo_load_data | 4.30 |
| pyshacl_load_shapes | 0.58 |
| turbo_load_shapes | 0.49 |
| turbo_compile_shapes | 0.36 |
| oxigraph_store_handoff | 0.09 |

### rules-1000-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 41.53 |
| turbo_load_data | 45.17 |
| pyshacl_load_shapes | 0.66 |
| turbo_load_shapes | 0.62 |
| turbo_compile_shapes | 0.41 |
| oxigraph_store_handoff | 0.82 |

### rules-5000-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 217.41 |
| turbo_load_data | 294.80 |
| pyshacl_load_shapes | 0.62 |
| turbo_load_shapes | 0.62 |
| turbo_compile_shapes | 0.39 |
| oxigraph_store_handoff | 4.08 |

Compatibility remains incomplete; this benchmark only certifies the displayed workloads. Native OWL-RL coverage is still being expanded. No result here establishes 100% pySHACL compatibility.
