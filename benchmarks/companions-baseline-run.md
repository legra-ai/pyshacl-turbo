# Companion turbo project benchmarks

Serial isolated workers. One warmup then retained timing samples; inputs rebuilt outside timers. Pipeline includes data parsing, inference, RDFLib conversion and complete validation output; shapes prepared outside timer. Separate cold workers measure whole-process peak RSS immediately after one operation, before observation encoding, including interpreter, backend imports, fixtures and retained output. Setup high-water marks are recorded, not subtracted. No process startup, file I/O or correctness hashing in timings. Generalized reference triples remain visible; full-output speedups require every observation to agree. Phase times are independent and must not be summed. Conversions are unpaired diagnostics. No timing thresholds.

Measured 2026-10-16T22:15:44.976648+00:00; macOS-27.0.1-arm64-arm-64bit-Mach-O.

| Operation | Nodes | Reference ms | Turbo ms | Full-output speedup | Parity | Reference peak MiB | Turbo peak MiB |
|---|---:|---:|---:|---:|---|---:|---:|
| parse_turtle | 100 | 4.829 | 0.462 | 10.45× | equal | 37.812 | 38.547 |
| parse_nquads | 100 | 3.680 | 0.445 | 8.28× | equal | 37.875 | 38.562 |
| serialize_nt | 100 | 0.559 | 0.046 | 12.24× | equal | 38.000 | 38.688 |
| serialize_nquads | 100 | 0.720 | 0.050 | 14.32× | equal | 38.125 | 38.438 |
| select | 100 | 4.474 | 0.290 | 15.44× | equal | 47.078 | 40.109 |
| select_named | 100 | 4.730 | 0.305 | 15.52× | equal | 47.328 | 40.094 |
| ask | 100 | 0.609 | 0.014 | 43.66× | equal | 46.719 | 39.438 |
| construct | 100 | 1.600 | 0.826 | 1.94× | equal | 46.922 | 40.516 |
| rdfs | 100 | 35.836 | 3.562 | — | standard_rdf_equal | 38.688 | 41.406 |
| owlrl | 100 | 96.149 | 8.531 | — | standard_rdf_equal | 39.250 | 42.984 |
| from_rdflib | 100 | — | 1.109 | — | diagnostic | — | 39.594 |
| to_rdflib | 100 | — | 2.855 | — | diagnostic | — | 42.344 |
| roundtrip | 100 | — | 3.777 | — | diagnostic | — | 42.875 |
| validate | 100 | 2.533 | 3.361 | — | report_graph_equal | 46.422 | 41.844 |
| pipeline_rdfs | 100 | 42.563 | 11.509 | — | different | 47.328 | 49.188 |
| pipeline_owlrl | 100 | 101.202 | 18.356 | — | different | 47.422 | 52.000 |
| parse_turtle | 1000 | 46.657 | 5.038 | 9.26× | equal | 42.156 | 43.766 |
| parse_nquads | 1000 | 34.869 | 5.036 | 6.92× | equal | 45.719 | 44.969 |
| serialize_nt | 1000 | 5.086 | 0.405 | 12.57× | equal | 42.891 | 44.125 |
| serialize_nquads | 1000 | 6.695 | 0.475 | 14.11× | equal | 44.828 | 43.969 |
| select | 1000 | 25.194 | 2.535 | 9.94× | equal | 51.875 | 47.344 |
| select_named | 1000 | 24.890 | 2.629 | 9.47× | equal | 53.438 | 47.406 |
| ask | 1000 | 0.613 | 0.014 | 42.74× | equal | 50.672 | 44.625 |
| construct | 1000 | 10.442 | 9.281 | 1.13× | equal | 52.219 | 52.578 |
| rdfs | 1000 | 394.469 | 31.721 | — | standard_rdf_equal | 48.953 | 62.188 |
| owlrl | 1000 | 627.858 | 63.398 | — | standard_rdf_equal | 50.266 | 72.672 |
| from_rdflib | 1000 | — | 10.570 | — | diagnostic | — | 49.156 |
| to_rdflib | 1000 | — | 26.601 | — | diagnostic | — | 75.500 |
| roundtrip | 1000 | — | 36.823 | — | diagnostic | — | 80.188 |
| validate | 1000 | 21.954 | 30.314 | — | report_graph_equal | 52.625 | 56.734 |
| pipeline_rdfs | 1000 | 448.308 | 111.398 | — | different | 54.609 | 106.703 |
| pipeline_owlrl | 1000 | 690.525 | 150.096 | — | different | 56.078 | 116.438 |

Raw samples, complete observations, package versions and source hashes are in the adjacent JSON file.
These deterministic synthetic workloads do not establish complete compatibility or predict application performance.

Raw evidence: [compressed JSON](companions-baseline-run.json.gz).
