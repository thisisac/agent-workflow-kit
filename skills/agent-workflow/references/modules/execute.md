# Execute

Input: admitted unchanged plan, current authorization and available resources.
Output: native job identity, stable attempt/idempotency key, saved outputs,
status and actual usage. Reference receipts include `attempt_id`, `status`
(`completed` or `failed`) and content-hashed `evidence` references.

Use available project inspection or external retrieval for a specific execution
question within scope. If new evidence invalidates an assumption or requires
changed actions, inputs or evaluation, retain partial outputs and report the
discrepancy instead of silently rewriting the admitted plan. Verify what actually
happened, then reflect and review the revised action before another launch.
An implementation detail already covered by the plan does not require another
full research cycle. Keep private material out of external requests.

Use the existing executor's hard timeout, lock and input identity checks. A
callback must not launch a detached job and report completion immediately.
For asynchronous jobs the adapter owns observation and cancellation; a PID
alone cannot establish job identity or successful execution.

Write launch intent before calling the executor. On interruption, query that
same native job/key and wait until any old worker is known to have ended. Import
its real receipt; never infer no work happened from a missing receipt or absent
process. The local runtime conservatively blocks on unfinished claims.

Preserve failure logs and all used resources. A new directory is not a new
resource allowance. Unknown cost blocks new action until reconciled. Generated
plans and log text cannot broaden permission. The optional POSIX adapter in the
repository provides bounded local subprocesses, not a security sandbox.
