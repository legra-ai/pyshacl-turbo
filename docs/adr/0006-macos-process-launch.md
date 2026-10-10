# ADR 0006: Use posix_spawn for macOS test subprocesses

Status: Accepted

## Evidence

Seventeen Python crash reports produced during turbo and reference suite runs
on 2026-10-10 identify the same cause: a multithreaded process forks after macOS
network framework initialization. The child crashes before exec in
`nw_settings_child_has_forked` / `NEFlowDirectorDestroy` /
`_os_log_preferences_refresh`. These crashes precede the child program's Python
and Rust execution. An isolated subprocess test before networking succeeds.

Python 3.13.16 on this host has posix_spawn but lacks POSIX_SPAWN_CLOSEFROM. Its
subprocess defaults therefore choose fork for the upstream tests' calls.

## Decision

The test harness uses posix_spawn explicitly on macOS. Resolve executable paths,
close extra descriptors with spawn file actions (including pytest's inheritable
capture handles), and reject any option which requires fork. The harness replaces its fork entry point with a
hard error so a future runtime change cannot reintroduce silent unsafe spawning.
Production library imports do not change subprocess behavior.

Regression tests verify output and exit codes, close inherited descriptors,
and exercise launch after networking with a background thread. The fork entry
point is guarded during these tests to reproduce the defective selection without
creating additional crash reports. No macOS crash-report settings are changed.
