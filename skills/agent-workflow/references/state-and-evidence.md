# State and evidence contract

These portable file conventions are not themselves a runtime implementation. The repository's optional reference runtime implements a separate conditional module contract described in `docs/runtime.zh-CN.md` in the full kit; it is not required to use this installed skill. Existing databases, queues, and scheduler records may supply the same facts; do not duplicate them merely to match filenames.

```text
.agent-workflow/<task-id>/
  workflow.json        goal, acceptance, authorization, limits
  state.json           compact current view, revision, attempt, next action
  events.jsonl         meaningful transitions and evidence references
  attempts/<id>/       plan, launch receipt, logs, outputs, verification
```

Resolve paths relative to the task directory unless specified otherwise. Select the task explicitly when several exist; do not choose by directory modification time. The contract defines constraints; executor receipts establish what ran; identity-bound results establish outcomes; state summarizes those facts. Reconcile conflicts and record corrections.

Scope facts to their task/attempt and source revision. Keep current status, cumulative accounting, historical observations, and future plans distinguishable. On a phase change, update the current action and observation time together; a preserved training instruction must not continue to describe an exited job. If records change while inspecting them, refresh before making a dependent decision. A compact projection should retain source identities and report conflicts rather than silently override them or become a second authority.

Track current user scope separately from execution phase: a stopped executor and an active planning-only review can coexist. A newer pause or narrower user instruction is not undone by an older authorization record, an empty GPU, a ready plan, or an idle escalation reminder. A view that reports no restriction has not granted permission; source instructions and actual controls still govern execution.

For long histories, prefer parent references to immutable originals over nested copies. Preserve existing ledgers and their failures/unknowns. If an existing executor requires nested records, first add a read-only view; migrate only after validating accounting, consumers, and controls. A smaller view reduces reading burden, not actual compute cost by itself.

## Phases

The table below is the host-neutral vocabulary. The optional runtime uses
RESEARCH → PLAN → REVIEW → EXECUTE → VERIFY → REFLECT (with deterministic continuation) as its module
phases, with separate ready/blocked/waiting/done status and pause/plan-only/execute
user mode. EXECUTE is the intent/receipt stage, not proof of a live training job.
Bind an existing host's equivalent states explicitly rather than copying labels.

| Phase | Meaning | Next decision |
|---|---|---|
| OBSERVE | Establish actual facts | RUNNING, VERIFY, DIAGNOSE, PLAN, or wait/stop |
| PLAN | Prepare the next action | READY once evidence, scope, resources, and checks suffice |
| READY | An authorized action can execute | RUNNING on real launch receipt; reconcile ambiguous launch |
| RUNNING | Executor is active | Observe milestones; VERIFY on exit; DIAGNOSE on error |
| VERIFY | Check saved output | REFLECT, DIAGNOSE, or DONE if overall acceptance is met |
| REFLECT | Interpret evidence and decide | PLAN, WAITING, BLOCKED, or DONE |
| DIAGNOSE | Locate a concrete failure | PLAN a justified repair, VERIFY, or BLOCKED |
| WAITING | No action due before a named condition/time | OBSERVE when due |
| PAUSED | Applicable user/project pause | Resume through the control rules |
| BLOCKED | Required input, permission, or capability missing | OBSERVE after unblocking or agreed recheck |
| DONE | Goal achieved or explicit terminal outcome recorded | No new attempts without changed objective/authorization |

STOP overrides normal progression and preserves evidence. Record the actual terminal reason; stopping does not mean the goal was achieved. Changing a phase on paper never creates execution evidence.

## Recovery and enforcement

For background jobs or repeat-unsafe operations, use stable attempt IDs, input/code/configuration identities, launch intent, and executor receipts. Ordinary reversible edits do not need these launch records. For local jobs distinguish PID reuse with start time, command identity, and boot identity where available. Remote jobs use native run IDs. Completion binds exit status and outputs to the same attempt.

Use real timeouts and resource locks. A PID file or JSON limit is not enforcement. For several writers/machines use an appropriate transaction/queue/lease system. Lease expiry requires reconciliation of the old worker before another launch.

A crash between intent and receipt requires scheduler/process/output inspection. A crash between side effect and event commit requires an idempotency-key query or external-result reconciliation. If neither is supported, mark the outcome uncertain and stop dependent side effects. This kit does not guarantee exactly-once effects.

Evidence may be a content-hashed path, immutable CI URL plus commit, or native result ID with version/retrieval information. Keep secrets, signed URLs, and private transcripts out of public examples.

## Events and accounting

A material event has a unique `event_id`, UTC timestamp, task/attempt ID, event type, evidence references, and decision. Append events for transitions, not a full history on every poll. Save real usage changes even when no notification is warranted.

Example shape (values must come from actual evidence):

```json
{"event_id":"attempt-001/check-001","at":"2026-11-10T12:00:00Z","task_id":"example-task","attempt_id":"attempt-001","type":"verification_failed","evidence":[{"path":"attempts/attempt-001/check.json","sha256":"<actual digest>"}],"decision":"Diagnose the missing partition.","cost":{"resource":"worker_seconds","value":null,"unit":"s","scope":"attempt","includes":[]}}
```

Unknown values are `null` with explanation, not zero. Distinguish attempt and campaign limits. Charge partial and failed execution. An outer duration that includes phases must not be summed with those phases; record what it includes. A child refers to the campaign's remaining accounting instead of resetting it. Explicitly authorized open-ended campaigns still retain per-action limits and stop controls.

Track stable notification keys and delivery outcomes. A local `notified` field is not proof of external delivery; host retries can duplicate notifications. Exact-once delivery needs service support and transactional design beyond this kit.
