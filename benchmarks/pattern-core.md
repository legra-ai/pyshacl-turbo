# Performance comparison

Measured 2026-10-10T23:34:21.243983+00:00; macOS-27.0.1-arm64-arm-64bit-Mach-O; Python 3.13.16.

Warm median milliseconds. RDFLib graph input and complete RDFLib report output; Turbo includes compilation and all conversions. Reused shapes exclude compilation but still include inference. Process startup, fixture construction and file I/O are excluded. Every timed workload first passed complete report-graph isomorphism against pySHACL. These are synthetic cases, not the private workload in the screenshot.

7 interleaved samples per configuration; raw samples and source hashes are in [pattern-core.json](pattern-core.json). A larger speedup is better. Measurements are descriptive, not a confidence interval.

| Workload | Data triples | Shape triples | Results | pySHACL ms | Turbo ms | Reused ms | Speedup | Reused speedup |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| core-100-nodes-1-shapes | 290 | 10 | 10 | 4.70 | 3.73 | 3.48 | 1.26× | 1.35× |
| core-1000-nodes-1-shapes | 2,900 | 10 | 100 | 45.10 | 34.81 | 31.84 | 1.30× | 1.42× |
| core-10000-nodes-1-shapes | 29,000 | 10 | 1,000 | 449.51 | 348.32 | 350.58 | 1.29× | 1.28× |

## Existing PyOxigraph Store input

Both engines receive an already loaded Store. Initial Store loading is excluded; the Python-to-Rust handoff, validation and RDFLib report construction are included. Turbo's handoff uses native N-Quads serialization and parsing; it avoids an intermediate RDFLib data graph but is not zero-copy.

| Workload | pySHACL ms | Turbo ms | Turbo reused ms | Store-to-store speedup |
|---|---:|---:|---:|---:|
| core-100-nodes-1-shapes | 8.52 | 2.61 | 2.36 | 3.26× |
| core-1000-nodes-1-shapes | 308.66 | 22.88 | 22.62 | 13.49× |
| core-10000-nodes-1-shapes | 28982.36 | 258.40 | 257.68 | 112.16× |

A dash means pySHACL's Store reasoning failed on a literal subject; the exact exception is recorded in JSON. No speedup is assigned to an unavailable backend.

## Loading, compilation and reasoning

Independent phase timings are diagnostic and must not be summed into the end-to-end figures. Reference loading uses RDFLib's Turtle parser. Turbo loading includes its Rust parser and conversion to RDFLib. Inference timings include a fresh copy of the data.

### core-100-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 5.21 |
| turbo_load_data | 5.39 |
| pyshacl_load_shapes | 0.42 |
| turbo_load_shapes | 0.34 |
| turbo_compile_shapes | 0.21 |
| oxigraph_store_handoff | 0.09 |

### core-1000-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 50.81 |
| turbo_load_data | 52.45 |
| pyshacl_load_shapes | 0.45 |
| turbo_load_shapes | 0.36 |
| turbo_compile_shapes | 0.27 |
| oxigraph_store_handoff | 0.95 |

### core-10000-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 632.05 |
| turbo_load_data | 694.93 |
| pyshacl_load_shapes | 0.58 |
| turbo_load_shapes | 0.45 |
| turbo_compile_shapes | 0.37 |
| oxigraph_store_handoff | 9.82 |

Compatibility remains incomplete; this benchmark only certifies the displayed workloads. Native OWL-RL coverage is still being expanded. No result here establishes 100% pySHACL compatibility.
