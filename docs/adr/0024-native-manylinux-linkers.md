# ADR 0024: Use native manylinux toolchains for Linux wheels

Status: Accepted

## Evidence

The Rust toolchain setup action v2 enables Cargo's `build.warnings=deny` policy.
Both Linux wheel jobs then fail because Rust passes `-Wl,-O1` to Zig 0.14.1,
which ignores that option and prints a deprecated linker optimization warning.
The previous action's `-D warnings` policy did not reject this linker message.
The failure occurs in the release build toolchain, independently of SHACL code.

## Decision

Build Linux wheels with the native GNU toolchain in the official PyPA
manylinux_2_28 containers, on matching x86-64 and ARM64 runners. GNU linkers
support Rust's linker optimization option. Keep Cargo warnings fatal; do not
suppress linker diagnostics or disable release optimization.

Use the pinned maturin backend through maturin-action, unpacking the verified
source archive into a separate build directory. Retain ADR 0019's exact-source
revision, glibc floor, artifact checks, native installation smoke tests and
publication gates. macOS and Windows retain their existing build path.

## Consequences

Linux wheel jobs require Docker and download the PyPA build images. They no
longer depend on Zig or cargo-zigbuild's translation of GNU linker options.
The setup action v2 upgrade must pass the complete release build matrix before
merging. Existing published artifacts remain immutable.
