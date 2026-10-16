# ADR 0026: Share function data snapshots within execution phases

Status: Accepted

Query preparation cloned the complete dataset for each focus node when SHACL
functions were registered. The snapshot only needs to change when the rule data
changes, or a new validation invocation begins.

Bind function callbacks to one reference-counted immutable dataset per rule
phase and per validation phase. Clone the reference for subsequent queries and
node-expression calls. Start a new snapshot after each rule commits, preserving
the existing rule visibility order and failure behavior. Constraint queries
which add a temporary shapes graph bind their own augmented dataset snapshot.
Target queries bind the data supplied to that target evaluation.

Do not cache snapshots in the compiled program or by mutable graph identity.
Callback registries, error state and recursion depth remain execution-local.
Native regressions verify reference sharing and phase refresh; Python regressions
verify that a subsequent rule sees earlier additions and that the next invocation
sees its own data. Existing function and callback-error tests remain required.
