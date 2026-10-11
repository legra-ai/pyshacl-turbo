# Performance comparison

Measured 2026-10-11T11:45:49.017163+00:00; macOS-27.0.1-arm64-arm-64bit-Mach-O; Python 3.13.16.

Warm median milliseconds. RDFLib graph input and complete RDFLib report output; Turbo includes compilation and all conversions. Reused shapes exclude compilation but still include inference. Process startup, fixture construction and file I/O are excluded. Every timed workload first passed complete report-graph isomorphism against pySHACL. These are synthetic cases, not the private workload in the screenshot.

7 interleaved samples per configuration; raw samples and source hashes are in [sparql-patterns.json](sparql-patterns.json). A larger speedup is better. Measurements are descriptive, not a confidence interval.

Load note: Other workspace Rust builds were active during this run. These interleaved samples describe performance under contention; they are not quiet-machine capacity measurements.

| Workload | Data triples | Shape triples | Results | pySHACL ms | Turbo ms | Reused ms | Speedup | Reused speedup |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| sparql-patterns-100-nodes-1-shapes | 300 | 7 | 10 | 695.43 | 5.40 | 5.24 | 128.79× | 132.77× |
| sparql-patterns-1000-nodes-1-shapes | 3,000 | 7 | 100 | 9504.48 | 62.27 | 65.26 | 152.63× | 145.63× |

## Existing PyOxigraph Store input

Both engines receive an already loaded Store. Initial Store loading is excluded; the Python-to-Rust handoff, validation and RDFLib report construction are included. Turbo's handoff uses native N-Quads serialization and parsing; it avoids an intermediate RDFLib data graph but is not zero-copy.

| Workload | pySHACL ms | Turbo ms | Turbo reused ms | Store-to-store speedup |
|---|---:|---:|---:|---:|
| sparql-patterns-100-nodes-1-shapes | 19.41 | 4.40 | 4.02 | 4.42× |
| sparql-patterns-1000-nodes-1-shapes | 655.08 | 42.80 | 42.13 | 15.30× |

A dash means pySHACL's Store reasoning failed on a literal subject; the exact exception is recorded in JSON. No speedup is assigned to an unavailable backend.

## Loading, compilation and reasoning

Independent phase timings are diagnostic and must not be summed into the end-to-end figures. Reference loading uses RDFLib's Turtle parser. Turbo loading includes its Rust parser and conversion to RDFLib. Inference timings include a fresh copy of the data.

### sparql-patterns-100-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 4.94 |
| turbo_load_data | 5.02 |
| pyshacl_load_shapes | 0.42 |
| turbo_load_shapes | 0.35 |
| turbo_compile_shapes | 0.27 |
| oxigraph_store_handoff | 0.11 |

### sparql-patterns-1000-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 74.61 |
| turbo_load_data | 62.93 |
| pyshacl_load_shapes | 0.46 |
| turbo_load_shapes | 0.34 |
| turbo_compile_shapes | 0.25 |
| oxigraph_store_handoff | 0.81 |

Compatibility remains incomplete; this benchmark only certifies the displayed workloads. Native OWL-RL coverage is still being expanded. No result here establishes 100% pySHACL compatibility.
