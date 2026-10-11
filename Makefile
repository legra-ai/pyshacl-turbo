PYTHON ?= python3.13
VENV_PYTHON := $(CURDIR)/.venv/bin/python
MATURIN := $(CURDIR)/.venv/bin/maturin
REGEX_MANIFEST := vendor/fancy-regex-0.19.2/Cargo.toml
SPARQL_MANIFEST := vendor/spareval-0.2.7/Cargo.toml

.PHONY: dev test test-compatibility test-regex test-sparql-evaluator test-coverage lint check benchmark benchmark-pipeline coverage

.venv/bin/python:
	uv venv --python $(PYTHON) .venv

dev: .venv/bin/python
	uv pip install --python $(VENV_PYTHON) -r requirements-test.lock maturin==1.15.0
	VIRTUAL_ENV=$(CURDIR)/.venv $(MATURIN) develop --release --locked

test:
	$(VENV_PYTHON) -m pytest -q
	PYO3_PYTHON=$(VENV_PYTHON) cargo test --workspace --locked

test-compatibility:
	$(VENV_PYTHON) -m pytest -q tests/test_w3c.py tests/test_w3c_documents.py tests/test_sparql.py::test_w3c_sparql_constraint --junitxml=w3c-results.xml
	$(VENV_PYTHON) scripts/check_upstream.py --output upstream-results.json

test-regex:
	cargo test --manifest-path $(REGEX_MANIFEST) --locked
	cargo test --manifest-path $(REGEX_MANIFEST) --locked --lib --no-default-features --features std,perf,unicode
	cargo test --manifest-path $(REGEX_MANIFEST) --locked --lib --no-default-features --features std,perf,unicode,python-re python_re_tests
	cargo fmt --manifest-path $(REGEX_MANIFEST) -- --check

test-sparql-evaluator:
	cargo test --manifest-path $(SPARQL_MANIFEST) --locked --lib
	cargo test --manifest-path $(SPARQL_MANIFEST) --locked --lib --features exact-custom-function-terms,undefined-functions-as-expression-errors

test-coverage:
	$(VENV_PYTHON) -m pytest -q --cov --cov-context=test --cov-report=term-missing --cov-report=xml:python-coverage.xml --cov-report=json:python-coverage.json --cov-report=html:htmlcov
	$(VENV_PYTHON) scripts/coverage_badge.py --input python-coverage.json --output htmlcov/coverage.svg

lint:
	./scripts/fmt.sh --check
	PYO3_PYTHON=$(VENV_PYTHON) cargo clippy --workspace --all-targets --locked -- -D warnings
	.venv/bin/ruff check python tests benchmarks scripts
	.venv/bin/ruff format --check python tests benchmarks scripts

check: test lint

benchmark:
	$(VENV_PYTHON) benchmarks/matrix.py --repeats 5 --output benchmarks/current.json

benchmark-pipeline:
	$(VENV_PYTHON) benchmarks/compare.py --nodes 100 1000 --repeats 5 --output benchmarks/latest.json

coverage:
	$(VENV_PYTHON) scripts/coverage_inventory.py
