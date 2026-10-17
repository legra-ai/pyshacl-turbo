PYTHON ?= python3.13
VENV_PYTHON := $(CURDIR)/.venv/bin/python
REGEX_MANIFEST := vendor/fancy-regex-0.19.2/Cargo.toml
SPARQL_MANIFEST := vendor/spareval-0.2.7/Cargo.toml

.PHONY: dev test test-compatibility test-regex test-sparql-evaluator test-coverage lint check benchmark benchmark-pipeline benchmark-targeting benchmark-preparation coverage

dev:
	uv sync --locked --extra test --python $(PYTHON) --reinstall-package pyshacl-turbo

test:
	uv run --locked --extra test pytest -q
	PYO3_PYTHON=$(VENV_PYTHON) cargo test --workspace --locked

test-compatibility:
	uv run --locked --extra test pytest -q tests/test_w3c.py tests/test_w3c_documents.py tests/test_sparql.py::test_w3c_sparql_constraint --junitxml=w3c-results.xml
	uv run --locked --extra test python scripts/check_upstream.py --output upstream-results.json
	uv run --locked --extra test python scripts/compare_contract.py --repeats 1 --output direct-contract.json --baseline docs/direct-contract.json

test-regex:
	cargo test --manifest-path $(REGEX_MANIFEST) --locked
	cargo test --manifest-path $(REGEX_MANIFEST) --locked --lib --no-default-features --features std,perf,unicode
	cargo test --manifest-path $(REGEX_MANIFEST) --locked --lib --no-default-features --features std,perf,unicode,python-re python_re_tests
	cargo +nightly-2026-10-16 fmt --manifest-path $(REGEX_MANIFEST) -- --check

test-sparql-evaluator:
	cargo test --manifest-path $(SPARQL_MANIFEST) --locked --lib
	cargo test --manifest-path $(SPARQL_MANIFEST) --locked --lib --features exact-custom-function-terms,undefined-functions-as-expression-errors,cached-query-plans

test-coverage:
	uv run --locked --extra test pytest -q --cov --cov-context=test --cov-report=term-missing --cov-report=xml:python-coverage.xml --cov-report=json:python-coverage.json --cov-report=html:htmlcov
	uv run --locked --extra test python scripts/coverage_badge.py --input python-coverage.json --output htmlcov/coverage.svg

lint:
	./scripts/fmt.sh --check
	PYO3_PYTHON=$(VENV_PYTHON) cargo clippy --workspace --all-targets --locked -- -D warnings
	uv run --locked --extra test ruff check python tests benchmarks scripts
	uv run --locked --extra test ruff format --check python tests benchmarks scripts

check: test lint

benchmark:
	uv run --locked --extra test python benchmarks/matrix.py --repeats 5 --output benchmarks/current.json

benchmark-pipeline:
	uv run --locked --extra test python benchmarks/compare.py --nodes 100 1000 --repeats 5 --output benchmarks/latest.json

.PHONY: benchmark-companions
.PHONY: test-rust-coverage
test-rust-coverage:
	uv run --no-project --python 3.13 python scripts/native_coverage.py

benchmark-companions:
	uv sync --project benchmarks --locked --no-build --python $(PYTHON)
	uv run --project benchmarks --locked --no-sync python -I benchmarks/companions.py --observation-encoder rdflib-v1 --nodes 100 1000 --repeats 5 --memory-repeats 3 --output benchmarks/companions-current.json
	uv run --project benchmarks --locked --no-sync python -I benchmarks/check_companions.py --report benchmarks/companions-current.json --baseline benchmarks/companions-baseline.json

benchmark-targeting:
	uv run --locked --extra test python benchmarks/targeting.py --nodes 1000 --shapes 10 --repeats 5 --output benchmarks/targeting.json

benchmark-preparation:
	uv run --locked --extra test python benchmarks/preparation.py --repeats 7 --output benchmarks/preparation.json

coverage:
	uv run --locked --extra test python scripts/coverage_inventory.py
