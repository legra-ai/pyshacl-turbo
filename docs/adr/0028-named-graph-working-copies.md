# ADR 0028: Avoid redundant named-graph rule copies

Status: Accepted

Validation previously materialized a union during rule expansion even if no
selected rule could run, then materialized another union for validation. Rule
expansion also copied the first materialized union to retain a before snapshot.

Skip rule-union construction when the selected shapes contain no active rules.
Still run the ordinary rule entry checks, including the positive iteration-limit
requirement. With active rules, execute against one materialized union and commit
the insertion-time delta from ADR 0027 only after successful expansion. This
removes the extra before/working copy and preserves original named graphs.

Validation retains a separate post-rule union, because rules can change the
dataset. Do not cache a union across mutable datasets or expose synthetic default
copies as caller data. A native work-count regression requires only the validation
union when no rule can run, and existing rule-delta/context/failure tests apply.
