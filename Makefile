PYTHON ?= python3.13
VENV_PYTHON := $(CURDIR)/.venv/bin/python
MATURIN := $(CURDIR)/.venv/bin/maturin

.PHONY: dev test lint check benchmark benchmark-pipeline coverage

.venv/bin/python:
	uv venv --python $(PYTHON) .venv

dev: .venv/bin/python
	uv pip install --python $(VENV_PYTHON) -r requirements-test.lock maturin==1.15.0
	VIRTUAL_ENV=$(CURDIR)/.venv $(MATURIN) develop --release --locked

test:
	$(VENV_PYTHON) -m pytest -q
	PYO3_PYTHON=$(VENV_PYTHON) cargo test --workspace --locked

lint:
	cargo fmt --all -- --check
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
