# Performance comparison

Measured 2026-10-10T15:47:32.809963+00:00; macOS-27.0.1-arm64-arm-64bit-Mach-O; Python 3.13.16.

Warm median milliseconds. RDFLib graph input and complete RDFLib report output; Turbo includes compilation and all conversions. Reused shapes exclude compilation but still include inference. Process startup, fixture construction and file I/O are excluded. Every timed workload first passed complete report-graph isomorphism against pySHACL. These are synthetic cases.

5 interleaved samples per configuration; raw samples and source hashes are in [performance.json](performance.json). A larger speedup is better. Measurements are descriptive, not a confidence interval.

| Workload | Data triples | Shape triples | Results | pySHACL ms | Turbo ms | Reused ms | Speedup | Reused speedup |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| core-100-nodes-1-shapes | 290 | 10 | 10 | 4.08 | 6.60 | 6.55 | 0.62× | 0.62× |
| core-1000-nodes-1-shapes | 2,900 | 10 | 100 | 58.42 | 84.15 | 87.35 | 0.69× | 0.67× |
| core-10000-nodes-1-shapes | 29,000 | 10 | 1,000 | 368.97 | 739.30 | 642.89 | 0.50× | 0.57× |
| shapes-1000-nodes-10-shapes | 2,900 | 82 | 1 | 1.37 | 15.25 | 14.27 | 0.09× | 0.10× |
| shapes-1000-nodes-100-shapes | 2,900 | 802 | 10 | 17.35 | 59.65 | 47.02 | 0.29× | 0.37× |
| shapes-1000-nodes-1000-shapes | 2,900 | 8,002 | 100 | 132.69 | 197.32 | 67.37 | 0.67× | 1.97× |
| rules-100-nodes-1-shapes | 290 | 22 | 10 | 145.24 | 5.32 | 4.34 | 27.29× | 33.44× |
| rules-1000-nodes-1-shapes | 2,900 | 22 | 100 | 1268.07 | 41.23 | 40.52 | 30.75× | 31.29× |
| rules-5000-nodes-1-shapes | 14,500 | 22 | 500 | 9804.41 | 264.36 | 322.40 | 37.09× | 30.41× |
| rdfs-100-nodes-1-shapes | 292 | 10 | 10 | 43.17 | 23.17 | 24.16 | 1.86× | 1.79× |
| rdfs-1000-nodes-1-shapes | 2,902 | 10 | 100 | 370.67 | 214.01 | 211.49 | 1.73× | 1.75× |
| owlrl-100-nodes-1-shapes | 291 | 10 | 10 | 111.30 | 47.89 | 44.49 | 2.32× | 2.50× |
| owlrl-1000-nodes-1-shapes | 2,901 | 10 | 100 | 1305.08 | 433.76 | 365.68 | 3.01× | 3.57× |

## Loading, compilation and reasoning

Independent phase timings are diagnostic and must not be summed into the end-to-end figures. Reference loading uses RDFLib's Turtle parser. Turbo loading includes its Rust parser and conversion to RDFLib. Inference timings include a fresh copy of the data.

### core-100-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 9.24 |
| turbo_load_data | 13.21 |
| pyshacl_load_shapes | 0.44 |
| turbo_load_shapes | 0.50 |
| turbo_compile_shapes | 0.25 |

### core-1000-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 47.88 |
| turbo_load_data | 78.22 |
| pyshacl_load_shapes | 0.55 |
| turbo_load_shapes | 0.49 |
| turbo_compile_shapes | 0.28 |

### core-10000-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 1125.11 |
| turbo_load_data | 1257.91 |
| pyshacl_load_shapes | 0.56 |
| turbo_load_shapes | 0.55 |
| turbo_compile_shapes | 0.26 |

### shapes-1000-nodes-10-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 79.38 |
| turbo_load_data | 81.89 |
| pyshacl_load_shapes | 1.55 |
| turbo_load_shapes | 1.51 |
| turbo_compile_shapes | 1.11 |

### shapes-1000-nodes-100-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 66.49 |
| turbo_load_data | 96.22 |
| pyshacl_load_shapes | 10.95 |
| turbo_load_shapes | 10.75 |
| turbo_compile_shapes | 9.45 |

### shapes-1000-nodes-1000-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 47.31 |
| turbo_load_data | 85.41 |
| pyshacl_load_shapes | 171.70 |
| turbo_load_shapes | 242.75 |
| turbo_compile_shapes | 144.15 |

### rules-100-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 4.30 |
| turbo_load_data | 4.70 |
| pyshacl_load_shapes | 0.65 |
| turbo_load_shapes | 0.64 |
| turbo_compile_shapes | 0.29 |

### rules-1000-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 40.11 |
| turbo_load_data | 44.77 |
| pyshacl_load_shapes | 0.71 |
| turbo_load_shapes | 0.66 |
| turbo_compile_shapes | 0.30 |

### rules-5000-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 275.08 |
| turbo_load_data | 385.76 |
| pyshacl_load_shapes | 0.88 |
| turbo_load_shapes | 0.73 |
| turbo_compile_shapes | 0.33 |

### rdfs-100-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 4.69 |
| turbo_load_data | 4.69 |
| pyshacl_load_shapes | 0.51 |
| turbo_load_shapes | 0.47 |
| turbo_compile_shapes | 0.26 |
| pyshacl_reasoning_including_copy | 30.32 |
| turbo_reasoning_including_copy_and_conversion | 17.12 |
| pyshacl_validation_after_reasoning | 4.15 |
| turbo_validation_after_reasoning_reused_shapes | 7.56 |

Inferred graphs: pySHACL 598 triples; Turbo 514. Entire inferred graphs isomorphic: **False**.
Validation reports agree for this workload, but the complete inferred graphs differ. This row does **not** establish equivalent reasoning coverage or a like-for-like reasoner speedup.

### rdfs-1000-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 41.79 |
| turbo_load_data | 45.56 |
| pyshacl_load_shapes | 0.55 |
| turbo_load_shapes | 0.48 |
| turbo_compile_shapes | 0.29 |
| pyshacl_reasoning_including_copy | 312.36 |
| turbo_reasoning_including_copy_and_conversion | 136.25 |
| pyshacl_validation_after_reasoning | 39.00 |
| turbo_validation_after_reasoning_reused_shapes | 71.01 |

Inferred graphs: pySHACL 5,818 triples; Turbo 4,924. Entire inferred graphs isomorphic: **False**.
Validation reports agree for this workload, but the complete inferred graphs differ. This row does **not** establish equivalent reasoning coverage or a like-for-like reasoner speedup.

### owlrl-100-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 5.11 |
| turbo_load_data | 4.55 |
| pyshacl_load_shapes | 0.59 |
| turbo_load_shapes | 0.49 |
| turbo_compile_shapes | 0.25 |
| pyshacl_reasoning_including_copy | 113.46 |
| turbo_reasoning_including_copy_and_conversion | 21.75 |
| pyshacl_validation_after_reasoning | 4.20 |
| turbo_validation_after_reasoning_reused_shapes | 9.72 |

Inferred graphs: pySHACL 696 triples; Turbo 516. Entire inferred graphs isomorphic: **False**.
Validation reports agree for this workload, but the complete inferred graphs differ. This row does **not** establish equivalent reasoning coverage or a like-for-like reasoner speedup.

### owlrl-1000-nodes-1-shapes

| Phase | Median ms |
|---|---:|
| pyshacl_load_data | 40.76 |
| turbo_load_data | 51.67 |
| pyshacl_load_shapes | 0.55 |
| turbo_load_shapes | 0.47 |
| turbo_compile_shapes | 0.28 |
| pyshacl_reasoning_including_copy | 589.69 |
| turbo_reasoning_including_copy_and_conversion | 166.11 |
| pyshacl_validation_after_reasoning | 36.75 |
| turbo_validation_after_reasoning_reused_shapes | 70.60 |

Inferred graphs: pySHACL 5,916 triples; Turbo 4,926. Entire inferred graphs isomorphic: **False**.
Validation reports agree for this workload, but the complete inferred graphs differ. This row does **not** establish equivalent reasoning coverage or a like-for-like reasoner speedup.

Compatibility remains incomplete; this benchmark only certifies the displayed workloads. Native OWL-RL coverage is still being expanded. No result here establishes 100% pySHACL compatibility.
