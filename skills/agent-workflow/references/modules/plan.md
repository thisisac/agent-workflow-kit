# Plan

Input: alternatives and relevant verified evidence. Output: the smallest useful
action with hypothesis, falsifier, input/evaluation identities, acceptance and
total resource estimate. Use the [action brief](../../assets/action-plan.md)
only to the detail the action needs.

Planning may inspect project files and consult external sources through the
host's available read-only tools. Resolve the concrete gap before committing to
an implementation: identify the actual caller/configuration for a local issue,
or check the relevant documented method/version for an external assumption.
Reuse research already applicable to the plan; do not treat its summary as
complete if local evidence contradicts it. Record the decisive sources and how
they support the chosen change. Optional `basis` records may use `source`,
`location`, `observation`, `supports`, and `limits`; no extra schema is required.

Do not carry out the proposed experiment or optimization while drafting it.
If only an experiment can resolve an uncertainty, propose that bounded test as
the next action with its own checks and limits. When the main approach is no
longer supported, return to research rather than patch the plan indefinitely.

For deliberate work the runtime plan fields are `approach`, `change`, `inputs`, `evaluation`,
`hypothesis`, `falsifier`, `action`, `estimated_cost`, `estimated_seconds`, and
`estimated_bytes`. Identify actual code/configuration changes in the change
record; labels do not substitute for a source revision in a real executor.

Estimate loading, startup, execution, periodic checks, output retention and final
verification. State uncertainty rather than presenting a reserve factor as a
guarantee. Choose fixed training length versus fixed time according to the
question; do not silently change the comparison after seeing outcomes.

For a claimed improvement, identify the baseline, what changes, what stays
comparable, the metric and acceptance rule, and the result that would count
against the hypothesis. State whether the action is exploratory or a planned
confirmation. Separate an expected benefit from evidence that it already works.

For learning, the action might be a short exercise with an independent check.
For development it might be one repair with a regression test. No new experiment
is required if the goal can already be verified from saved evidence.

For explicitly routine work, hypothesis and falsifier are optional, and no new
research or independent review is required. The plan still identifies the
action, inputs, evaluation and resource estimates; deterministic scope, identity
and limit checks remain. See [parameters](../parameters.md).
