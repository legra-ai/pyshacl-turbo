# Repository instructions

- Use native uv project commands throughout: `uv add`, `uv sync --locked` and
  `uv run --locked` (including Ruff, mypy and pytest). Keep dependencies in
  pyproject.toml and uv.lock. Do not use pip, uv pip, tox or standalone tool installs.
- Build source distributions and wheels with `uv build`; install test artifacts
  in isolated uv projects using `uv add` and `uv sync`. Keep native wheels as the
  build inputs for wheel verification and coverage; never substitute source imports.
- Use `uv publish` for package publication through the tested trusted-publisher CI.
