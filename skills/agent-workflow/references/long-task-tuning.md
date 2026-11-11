# Improve a workflow already in use

An existing training or development loop is a usable field case. First establish which steps actually executed, what evidence survives, and where continuation failed. Do not dismiss it because it is private or not yet a reusable demo. Keep these claims separate:

- **Field operation:** a real task ran through recorded stages.
- **Retrospective finding:** inspection identifies a specific inconsistency or bottleneck.
- **Reproduction:** a controlled check reproduces that failure with a narrow input.
- **Measured improvement:** a comparable before/after run shows a changed outcome or cost.

One level does not imply the next. A static patch or synthetic check must not be presented as successful production recovery.

## Inspect the decision path

Follow the selected task pointer to its current executor and result authority. Compare status, current action, attempt identity, and observation time. Inspect the native process/job status when relevant. Read failure output and completed stage receipts; do not load a model, rerun evaluation, or restart a job just to review the workflow.

Ask which delay or wrong decision each proposed change would remove. Common useful changes are a smaller current view, evidence-linked decisions, better error context, and reliable completion handoff. Fix a demonstrated mismatch before adding a new controller or more instructions. Reuse existing diagnostic work.

## Keep execution and decisions connected

The executor handles bounded compute, saved milestones, and agreed verification stages. The agent interprets those outputs and selects the next authorized action. Use completion events where the host supports them, with periodic inspection as a fallback. A callback that writes `complete` is evidence of a transition, not proof that another agent was awakened.

During a long run, prepare only independent work that changes the pending decision: a supported alternative, a concrete repair, or a missing-fact check. At the result milestone, revisit the prepared plan against the new evidence. A plan prepared before the result is not automatically still valid. Do not modify a fixed experimental recipe midway to improve utilization.

## Make failures useful

Preserve the original exception type, message, traceback location, phase, attempt/job identity, child exit status, and log references before cleanup can obscure them. Include observed values for failed checks when available, avoiding credentials and sensitive inputs. Keep the first failure distinct from a later cleanup error. Missing original evidence remains unknown; do not recreate a failure and claim it was the historical cause.

Review whether this is already captured. If not, prepare the smallest change to the next authorized executor version and check that it preserves stop, accounting, and cleanup behavior. Do not edit an active or immutable executor to retrofit the past.

## Synthetic training walkthrough

The following is invented, not a user result or a runnable training program:

| Saved observation | Correct decision | Workflow improvement to check |
|---|---|---|
| Experiment `sample-b` has a saved midpoint comparison, no error, fixed recipe still active | Interpret the evidence; continue the agreed recipe | Prepare a distinct next proposal without touching this run |
| Final weights, fixed evaluation, and independent result checks all exist for `sample-a` | Summarize verified tradeoffs and decide whether to retain | Reuse valid results instead of another expensive evaluation |
| Current executor says stopped; a summary still says training | Reconcile current source and native job status; report the conflict | Update phase/action together and scope inherited fields |
| Generic failure text has no originating location | Preserve uncertainty and inspect existing logs/diagnostic receipts | Capture original exception context prospectively |
| One attempt ended but the continuing objective remains open | Check the supported next action and actual continuation mechanism | Distinguish stage completion from goal completion and monitor lifecycle |

Judge an optimization by decision latency, duplicate work, false completion claims, unnecessary permission requests, valid progress, and measured overhead. Use the same inputs and host for comparisons where possible. A field case supports grounded design, while causal performance claims still need an appropriate comparison.
