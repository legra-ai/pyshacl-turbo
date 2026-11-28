# ADR 0049: Serve `import pyshacl` by default through a start-up import alias

Status: Accepted

## Evidence

pyshacl-turbo is advertised as a drop-in replacement for pySHACL, but code had
to be edited from `import pyshacl` to `import pyshacl_turbo`, and the commands
were named `pyshacl-turbo`. Two packaging constraints rule out the obvious
fixes:

- A wheel cannot ship a top-level `pyshacl/` package. pip installs the real
  `pyshacl` distribution whenever another package depends on it, and the two
  wheels' files would then overwrite each other in `site-packages`.
- We do not own the PyPI name `pyshacl`, and a separate alias distribution
  would still lose to, or collide with, a transitively installed pySHACL.

The pySHACL upstream suite previously reached Turbo through a test-only bridge
that monkeypatched the installed pySHACL. That bridge also mapped
`ConstraintLoadError`, `ShapeLoadError` and `RuleLoadError` to `ValueError`, so
the suite could not see that Turbo raised a plain `ValueError` where pySHACL
raises `ConstraintLoadError` (upstream `issues/test_058`).

Measured on macOS 27 arm64, CPython 3.13, with pySHACL 0.40.2 installed beside
the wheel: `python -c pass` takes a median of 24.5 ms with the hook and 23.3 ms
without it over 40 runs (within run-to-run noise); `-X importtime` attributes a
median of 0.66 ms to the hook module. Importing the hook loads neither rdflib
nor pyshacl-turbo.

## Decision

**Drop-in is the default.** The pyshacl-turbo wheel installs, beside the
`pyshacl_turbo` package:

- `pyshacl_turbo_alias.py`, a standard-library-only module that defines an
  import alias and a `sys.meta_path` finder, and
- `pyshacl_turbo_alias.pth`, whose single line
  `import pyshacl_turbo_alias; pyshacl_turbo_alias.install()` runs when `site`
  processes `site-packages`.

`install()` inserts one `AliasFinder` at the front of `sys.meta_path`, ahead of
the path finder, so it wins even when the real pySHACL is installed. For
`pyshacl` and every `pyshacl.<sub>` name it imports
`pyshacl_turbo.compat[.<sub>]` and binds the alias to that same module object
(identity and `isinstance` agree). It also serves `python -m pyshacl` and
`python -m pyshacl.cli`. A name the compatibility package does not provide
(for example `pyshacl.sh_http`, the HTTP server) raises `TurboAliasError`, an
`ImportError` that names both distributions and the switch; it never falls
through to a mixture of the two packages.

**Off switch.** `PYSHACL_TURBO_ALIAS=0` turns this alias off;
`TURBO_ALIAS=0` turns off every turbo package's alias at once. The values `0`,
`false`, `no` and `off` (any case) mean off; anything else, or unset, means on.
The finder reads the environment on every lookup, so setting the variable
before the first `import pyshacl` suffices, including inside a running
process, and subprocesses inherit it. When off, the real pySHACL imports under
its own name. A `[tool.pyshacl-turbo]` configuration file setting is not
provided: reading project files at interpreter start-up would cost more than
the hook and depends on the working directory.

**Visible state.** `pyshacl.__turbo__ is True` only when the alias served the
import; the real pySHACL has no such attribute. `pyshacl.__turbo_version__` is
the installed pyshacl-turbo version. `pyshacl.__version__` is the mirrored
pySHACL API version, `0.40.2`, so version checks written against pySHACL keep
working.

**Surface.** `pyshacl_turbo.compat` mirrors pySHACL 0.40.2 at its import paths:
`validate`, `validate_each`, `shacl_rules`, `Validator`, `RuleExpandRunner`,
`Shape`, `ShapesGraph`, `__version__`; `pyshacl.entrypoints` (plus
`meta_validate`); `pyshacl.errors` (`ReportableRuntimeError`, `ShapeLoadError`,
`ConstraintLoadError`, `RuleLoadError`, `ValidationFailure`,
`ValidationWarning`, `ShapeRecursionWarning`, `ConstraintLoadWarning`);
`pyshacl.rdfutil` (`load_from_source`) and `pyshacl.rdfutil.load`
(`load_from_source`, `path_from_uri`); `pyshacl.graph_abstraction` (`DataGraph`, `RdfLibDataGraph`,
`has_oxigraph`); `pyshacl.validator_conformance` (`DASH`, `check_sht_result`,
`check_dash_result`, `extract_query_and_expected_result`,
`evaluate_query_testcase`); `pyshacl.validator`, `pyshacl.shape`,
`pyshacl.shapes_graph`, `pyshacl.rule_expand_runner`; `pyshacl.cli.main` and
`pyshacl.cli_rules.main`. pySHACL internals (constraint classes, `rdfutil`
clone/compare/stringify helpers, `sh_http`) are not mirrored.
`check_sht_result` unfolds both report descriptions through blank nodes, so a
path node shared by several results equals separate copies, and requires every
retained field and multiplicity to match.

**Commands.** The wheel installs `pyshacl` and `pyshacl_rules` as well as the
always-unambiguous `pyshacl-turbo` and `pyshacl-turbo-rules`. When the real
pySHACL is installed too, both write the same script files and the
distribution installed last owns them. Both owners' scripts import
`pyshacl.cli` / `pyshacl.cli_rules` by name, so either way the commands follow
the switch: Turbo with the alias on, the real pySHACL with it off (Turbo's
script exits with a message naming the switch when pySHACL is absent). The `pyshacl` command accepts
pySHACL's options, including `-q/--sparql-mode` (local inputs are rejected
with pySHACL's message; remote endpoints raise `NotImplementedError`, exit 3)
and `--server`/`PYSHACL_SERVER`, which exits 1 like a pySHACL without its
optional HTTP components.

**Differential gates keep comparing with pySHACL.** `tests/conftest.py`, the
Makefile, `scripts/provider_validation.py` and every workflow set
`PYSHACL_TURBO_ALIAS=0`. The upstream harness sets the switch per run instead
of monkeypatching: the turbo run sets it on and requires
`pyshacl.__turbo__`, the reference run sets it off and requires its absence.
The upstream suite's own `import pyshacl`, its `pyshacl.errors` classes and
its `pyshacl` / `pyshacl_rules` subprocesses therefore exercise the shipped
alias. `tests/cli_parity.py` runs representative commands through pySHACL and
through the alias (module and installed script) and compares exit codes and
reported conformance; every difference is a `pyshacl-cli` entry in
`tests/divergences.toml` (ADR 0047). The wheel acceptance check installs the
release wheel beside pySHACL 0.40.2 on Linux, macOS and Windows and checks the
alias on, both switches off, and both command names.

**Pattern for the other turbo packages (PH-37).** rdflib-turbo (`rdflib`) and
owlrl-turbo (`owlrl`) ship the same two files, named
`<package>_turbo_alias.py` and `<package>_turbo_alias.pth`, with a
`TurboAlias(name=..., target="<package>_turbo.compat", distribution=...,
switch="<PACKAGE>_TURBO_ALIAS")`, honour the shared `TURBO_ALIAS` switch with
the same off values, expose `<package>.__turbo__`, and keep the hook module
free of non-standard-library imports.

## Consequences

Installing pyshacl-turbo changes what `import pyshacl` means in that
environment, including for other installed packages that depend on pySHACL;
this is the advertised drop-in behaviour, detectable through `__turbo__` and
reversible with one variable.

Risks:

- The hook runs at every interpreter start. It must stay standard-library-only
  and constant-time; the 0.66 ms import is the budget to protect.
- Interpreters started with `-S`, embedded interpreters without `site`, and
  environments that skip or forbid executable `.pth` lines do not install the
  alias; `import pyshacl` then loads the real pySHACL if present. `-I` and `-E`
  still process `site-packages` `.pth` files. A future CPython that changes
  executable `.pth` lines requires moving the same `install()` call to its
  replacement.
- The `pyshacl` script files are owned by whichever distribution was installed
  last; `pyshacl-turbo` is the unambiguous command.
- Behaviour that differs from pySHACL is reachable under pySHACL's own name, so
  every difference must stay in `tests/divergences.toml`.
