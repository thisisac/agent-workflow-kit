# Verify results

Input: execution identity, output hashes, original acceptance and comparison
rules. Output: validity, every acceptance check, observed improvement, goal status,
and retained evidence. Reference callback data uses `valid`, `improved`,
`goal_met`, `checks` and `evidence`.

Prefer deterministic checks or an independent verifier over the same actor's
self-report. Confirm completeness and identity before interpreting a metric.
Check invariants and regressions, not only the selected improvement metric.
Compare against the specified baseline under the same rules; record limitations
such as one seed, exposed evaluation or an invalid comparison.

Hash validation establishes file identity, not scientific correctness. A clean
process exit does not prove the goal. A partial training checkpoint is not a
completed scheduled experiment. Reuse valid saved evaluation artifacts instead
of repeating expensive computation merely to refresh a status report.

For learning, verify recall or application without revealing the answer in the
exercise. For data work, verify coverage, schema, duplicates and output identity.
The overall goal is complete only when every required check passes.
