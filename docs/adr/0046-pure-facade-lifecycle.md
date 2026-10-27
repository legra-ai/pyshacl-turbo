# ADR 0046: Keep facade release and native owner verification separate

Status: Accepted for source integration; coordinated release CI remains gated.

The Python facade uses Hatchling and the provider owns its single Rust extension.
Build one universal wheel from the original facade source archive and require
that same wheel in Linux, macOS and Windows installed acceptance. Version the
facade with native uv metadata commands. Retire the dormant copied Rust engine,
vendor forks, native toolchains and native collector from this repository.

Retain the Python compatibility fixtures and reference license. Native identity,
datatype, storage, matcher, evaluator and coverage verification execute in an
independently byte-verified published provider source authority. Candidate inputs
remain a distinct explicit authority and cannot masquerade as published inputs.
Keep exact original source archives, wheel payload equality and complete native
fork identity, including the matcher, throughout verification.

The local matrix diagnostic hashes facade sources and the actually loaded native
module, checks shared compiler/engine identity, and records its compiled engine
fingerprint. It must not hash retired local Rust paths or claim independently
verified provider source authority. Mark these diagnostic reports ineligible for
performance publication; published benchmark preparation retains the full
original provider archive, wheel and source-verification contract.

Prepare, build, verify and publish the same prepared revision through ci.yml.
The pinned shared release planner must actually support a pure uv project;
missing planner or provider capabilities fail before publication or expensive
native tooling. This source integration does not authorize replacing immutable
archives, inventing a registry dependency floor, or bypassing required reviews.

Linting and commit hooks use the standalone locked `tools/dev` project. They
must not resolve the runtime source peer: a missing or changing provider is a
runtime verification failure, not a prerequisite for checking Python source.
The provider and publication gates remain mandatory.

This supersedes facade-local native build and collector ownership in ADRs 0024,
0032 and 0034, while retaining their original-archive and tested-wheel guarantees.
