# Parameters and tuning

Choose the simplest route that meets the task contract. These parameters describe
the optional Python runtime; the host-neutral JSON templates describe equivalent
concepts but are not accepted directly by `Workflow`.

## One effort choice

| `contract.effort` | Route | When to choose |
|---|---|---|
| `deliberate` (default when absent) | research → plan → review → execute → verify → reflect | New research, expensive work, consequential uncertainty or effects needing independent review |
| `routine` (explicit host choice) | plan → execute → verify; reflect on failure/incomplete acceptance | Known, cheap, reversible action with a reliable acceptance check |

There is no automatic risk classifier. The trusted host selects effort when
creating the contract; generated plans cannot downgrade it. Routine plan checks
cover scope, identity, repetition and limits, **not scientific merit**. Do not
select routine merely to get a rejected or expensive plan admitted.

In both routes a reflection decision `continue` reuses research and returns to
PLAN; `pivot` opens RESEARCH. After a routine pivot, that research and the separate
review apply to subsequent plans. `wait` needs a wake condition, `complete` needs
verified acceptance, and `stop` ends work. Routing occurs in the same transaction
as reflection, without a RESUME callback. Old RESUME states remain readable.
Routine acceptance completes without requiring an invented lesson; deliberate
reflection can still capture a justified lesson before completion.

## Required contract and limits

`task_id`, `goal`, `acceptance` (nonempty check-ID list), and `authorization`
(source plus allowed action names) must come from the actual task. The immutable
contract is stored once. Reopening with a changed contract is rejected; changing
limits requires an explicit host-level amendment design, not a new directory.
This alpha has no amendment API.

Every limit below is required. **No universal numeric defaults** are hidden in
the engine: a short exercise and an expensive batch job need different ceilings.
`demo.contract()` provides synthetic example values, not production presets.

| `limits` key | Type / unit | How to choose or adjust before starting |
|---|---|---|
| `max_cycles` | positive integer | Bound completed decision cycles and explicit replans; raise only when distinct useful attempts justify the cost |
| `max_family_attempts` | positive integer | Bound attempts sharing an approach; do not raise to rescue the same failed idea |
| `plateau_patience` | positive integer | Number of consecutive verified non-improvements before blocking approaches in that streak; if larger than the cycle limit it cannot trigger first |
| `max_cost` | positive finite number, one task-defined unit | Include reasoning, failed execution and verification; return actual usage, null for unknown |
| `max_seconds` | positive finite seconds | Sum of observed callback durations, not calendar deadline or provider hard timeout; allow final checks and reconcile costs honestly |
| `min_free_bytes` | positive finite bytes | Leave filesystem headroom for the host and retained outputs; this is a free-space admission check |
| `max_workspace_bytes` | positive finite bytes | Bound this runtime directory, including database and retained artifacts; reserve estimated next output |
| `max_workspace_files` | positive integer | Bound directory entries visited during launch scans; directories count too; this is not a whole-disk scan |

Budget and free-space checks run before reasoning/planning/review and launch.
The bounded directory traversal runs only at launch, avoiding repeated tree walks
between reasoning stages. Verification, reflection and reconciliation remain
available to account for ended work even when new work is no longer admitted.
Admission estimates are not hard quotas. Native executors must enforce their
real duration, storage and resource constraints.

## Plan and callback fields

All callbacks return `{data: {...}, cost: actual_number_or_null}`. Evidence uses
workspace-relative `path` plus `sha256`. Cost is separate from measured seconds;
never add the units or sum an inclusive receipt again with its nested usage.

Every plan needs `approach`, `change`, `inputs`, `evaluation`, `action`,
`estimated_cost`, `estimated_seconds`, `estimated_bytes`. Bind real revisions
and input/evaluation identities in the execution adapter. Deliberate plans also
require `hypothesis`, `falsifier` and membership in researched alternatives.
Routine plans may omit those two fields; they still need all acceptance checks.
See [module contracts](modular-workflow.md) for other callback outputs.

Research, plan and review data may include optional `basis` records with
`source`, `location`, `observation`, `supports` and `limits`. These preserve the
reason for a choice; they are not enforced source validation. Available project
roots, retrieval services, query bounds and disclosure permissions come from
the task and host tools, not a built-in search client. Include retrieval time
and actual fees in the existing callback accounting rather than inventing a
second allowance.

## Runtime and adapter settings

| Setting | Default / accepted values | Meaning and adjustment |
|---|---|---|
| `set_mode(mode, source)` | starts `plan_only`; execute / plan_only / pause / stop | Trusted host records real user scope. Pause stops future modules, not an already-running job; stop is terminal |
| `tick(handlers, expected_phase=None)` | one callback maximum | Optional phase check rejects stale routing; restart from saved state rather than replay |
| `build_graph(..., max_steps=14)` | positive integer | Work nodes per wake, not task budget; lower for short wakes. Caller must also supply an adequate LangGraph recursion limit |
| demo `--steps` | 6; integer 1–100 | Bounded CLI wake; use 6 per deliberate demo cycle or 3 for the routine example |
| demo `--effort` | deliberate / routine | Must match the existing task contract on later wakes; does not change an active task |
| demo `--langgraph` | off | Optional actual graph router; no second persistence authority |
| `run_local(..., timeout_seconds, max_output_bytes=...)` | explicit timeout; log cap 65,536 bytes | POSIX process-group time limit and retained stdout/stderr limit; not arbitrary-file, GPU or memory quotas |

Fixed implementation bounds are not extra user knobs: 32KiB callback output,
64KiB bridge request, 1MiB direct evidence file, four recent attempts in bridge
context, eight current lessons. Larger artifacts need a small manifest and a
real domain verifier, not a bypass of evidence checks. Model transport, model
choice, provider timeouts, notification channels and polling cadence belong to
the host; this kit exposes no pretend parameters for services it does not ship.

Tune using actual failed checks, duplicate effects, irrelevant work, calls,
latency and cost under fixed acceptance. Fewer steps alone do not establish
better decisions. Never tune thresholds on protected final evaluation results.

## Capability adaptation settings

These optional **host/skill instruction settings** govern
[skill evolution](skill-evolution.md). They are not `Workflow` constructor
parameters, engine-enforced quotas or a new resource allowance. Store choices
in the existing task contract/profile; the host enforces permissions and bounds.
The host-neutral `workflow.json` template includes these defaults.

| Setting | Default | Adjustment |
|---|---|---|
| `skill_discovery` | `on_gap` | Search only for an identified capability gap; choose `off` for offline or fixed-dependency work |
| `skill_change_scope` | `task` | Adapt the task profile; `proposal_only` records suggestions without adoption; `maintained_skill` permits candidate edits only when actual authorization covers the maintained skill |
| `max_skill_queries` | 2 per gap | Nonnegative integer; total external discovery queries across wakeups for the same gap; zero disables new discovery |
| `max_skill_candidates` | 3 per gap | Positive integer; bound the number of candidates inspected in depth |
| `max_skill_trials` | 1 per gap | Nonnegative integer; candidate revisions evaluated, not individual cases or repeats; zero leaves proposals only |

Choose bounds before discovery using task value and remaining resources. Charge
search, source review, trials and failures to the existing task accounting;
unknown usage stays unknown. Repeated wakeups and renamed gaps do not renew
these bounds. A changed goal or source can justify a new decision, with the
prior evidence retained. Scope selection never grants new authority or relaxes
acceptance. If meaningful evaluation cannot fit, defer the shared change.
