# Validation status — 0.3.4-alpha

Checked on 2026-11-11 on Linux with Python 3.11. These are software and synthetic runtime results, not agent-quality or scientific-performance scores.

The 0.3.4 update adds skill-discovery and workflow-evolution instructions,
references, host-neutral settings and five behavior specifications. Runtime code
and interfaces are unchanged. All 34 model behavior/activation specifications
remain unrun: 27 behavior and 7 activation cases. No autonomous self-improvement,
new/old skill advantage or domain-performance gain has been measured.

## Rechecked for 0.3.4

| Check | Observed result |
|---|---|
| Skill metadata validator | Skill accepted |
| Release/packaging suite | 14 tests passed, including installed-reference containment and prompt/rubric pairing |
| Full software suite with optional LangGraph | 48 tests passed, no skips; these exercise synthetic runtime behavior, not model-driven evolution |
| Public privacy and packaged-link checks | 61 source files, 0 reported errors, including the external private-term list |
| Discovery/source review | Public directory plus one CLI query; exact source snapshots reviewed for find-skills, skill-creator and improve-skill-quality; metadata in research/sources.json |
| Evolution behavior cases | Five new specifications; not executed against a model |

The host supplies skill discovery, installation, editing, evaluation and
revision selection. The reference engine does not enforce the new instruction
settings or provide a hot-swap/promotion API. A retained revision requires the
host to bind actual immutable skill bytes; a statement in a record is not an
implemented version lock. Candidate behavior must be evaluated in isolation
before claiming an improved shared skill.

## Rechecked for 0.3.3

| Check | Observed result |
|---|---|
| Exact installation commands in both READMEs | Installed complete skill bytes into isolated profiles; repeated installation preserved the existing copy by raising `FileExistsError` |
| Exact README demo commands | Each language's walkthrough ran in three separate processes and returned cycle 1 / ready, cycle 2 / ready, cycle 3 / done with the documented labels |
| Runtime guide routine command | Returned done / cycle 1 in each isolated workspace |
| Release/packaging suite | 14 tests passed |
| Public source privacy and packaged-link checks | 60 source files, 0 reported errors |
| Unchanged implementation | Runtime, test, skill and behavior-specification bytes match 0.3.2 |

These checks did not install into an actual user profile, configure a scheduler, invoke a model, or test notification delivery. The new monitoring setup scenarios are integration guidance, not completed host tests. Optional LangGraph execution was verified in earlier implementation checks below, not repeated for this documentation update.

## Retained checks from 0.3.2

- Release/packaging suite: 14 tests passed after the scope, module and evaluation-specification updates.
- Runtime engine and Python test sources match 0.3.1 byte for byte. Module text loaded by the bridge intentionally differs.
- Skill metadata validator accepted the revised skill. The 59-file public source scan, including the external private-term list and packaged-link checks, reported 0 errors.
- The specification inventory now has 22 behavior and 7 activation cases, each paired with a rubric. New cases cover investigation during planning, a method/project mismatch and same-session improvement work. These remain unrun model evaluations.

## Retained documentation checks from 0.3.1

| Check | Observed result |
|---|---|
| Exact installation command from both READMEs | Copied the complete skill into isolated destinations; a second invocation raised `FileExistsError` and preserved the existing installation |
| Exact deliberate CLI walkthrough | Three separate invocations returned `ready`/cycle 1, `ready`/cycle 2, then `done`/cycle 3 with the documented output |
| Exact routine CLI walkthrough | One invocation returned `done`/cycle 1 |
| Optional LangGraph routine route | Actual `langgraph==1.2.20` execution returned `done`/cycle 1 |
| Release test suite | 14 tests passed |
| Skill metadata and public source checks | Skill accepted; 59 source files scanned with 0 reported errors |

Installation and CLI checks used disposable synthetic workspaces. They did not install the skill into a real user profile or change a scheduler.

## Retained implementation checks from 0.3.0

| Check | Observed result |
|---|---|
| Environment-provided skill-creator `quick_validate.py` | Skill accepted; installed skill links also checked to remain inside its folder |
| Full software suite with optional `langgraph==1.2.20` | 48 tests passed, 0 failures, 0 skips |
| Standalone CLI, standard-library route | Three separate process wakeups continued one database and reached verified synthetic acceptance |
| Standalone CLI, actual LangGraph route | Three separate process wakeups continued one database and reached the same acceptance |
| Interrupted execution | Child exited after writing its output/receipt but before state commit; next wake refused relaunch; original receipt reconciled once |
| Concurrent wakeups | Second caller observed the durable claim without invoking the active module again |
| POSIX local process adapter | Short timeout killed the process group and saved failure; excess retained logs capped and explicitly marked truncated |
| State/policy checks | Planning and pause precedence, scope, immutable contract, duplicate identity, plateau pivot, cycle and cost admission, workspace headroom, unknown cost, changed evidence, and unsupported completion claims exercised |
| Proportional routing | Same synthetic plan/output/acceptance completed in six deliberate callbacks or three routine callbacks; routine failure/pivot and deliberate review safeguards exercised |
| Deterministic continuation | Reflection commits the next route without a RESUME callback; continue reuses research; legacy RESUME state routed without a host callback |
| Provider-neutral agent bridge | Scripted callbacks exercised request/module contracts and separate execution/verification; no model endpoint was invoked |
| Public release checks | 59 source files, 0 reported errors; personal-path/email/key/token patterns and an external private-term list checked against names and contents |
| Original release tests | Allowlist, per-file manifest hashes, sensitive-pattern rejection, symlinks, invalid files/links, and same-source byte reproducibility passed |

The 0.3.4 release ZIP adds one generated manifest to 61 public source files, for 62 members. The checked source snapshot includes the original reference-runtime implementation, module references and tests. Third-party source snapshots, dependency environments, private-term lists, local field observations, actual run databases, logs, models and datasets are excluded.

The main synthetic text demo is deliberately scripted: two case-only attempts fail a fixed check, then strip-and-case passes. It validates routing, persistence, policy and handoffs; it does not show an LLM independently discovered the pivot. The routine demo chooses the known passing transformation immediately; this is also scripted. The paired routing test uses the same passing plan, output hash and acceptance checks for both effort levels. It measures callback counts, not elapsed-time/token savings or model decision quality. The reasoning bridge test likewise checks the integration contract, not reasoning quality.

## What these checks do not establish

- None of the 22 agent behavior cases or 7 activation cases has been independently run against a model. Their expected actions remain specifications, not a pass rate.
- No paired old/new skill or no-skill comparison, token saving, task-success improvement, or scientific/model-performance gain was measured.
- No Deep Agents connector, real asynchronous queue, distributed lock, cloud job, scheduler, or notification delivery was tested. LangGraph routes actual nodes; SQLite is the reference runtime's single persistence authority.
- Python reasoning callbacks are not preempted by the engine. Providers need their own hard timeout. The POSIX command adapter limits its process group and retained stdout/stderr, not arbitrary files, detached processes, memory, GPU or network usage.
- Pause blocks future modules; active work requires native executor cancellation. Reconciliation is a trusted host operation and must not be called while an old worker could still run.
- Local Linux tests do not establish Windows behavior. The published 0.3.3 source passed Linux, Windows and optional LangGraph hosted CI at commit `e214d7a18422cc3525361377e4a1920d5a6c1750`. This does not establish behavior of model-driven workflow evolution.
- No real user project or data is included in this implementation, and no private workflow or scheduler was restarted. The reviewed public package was published separately; that publication is not a workflow-efficacy test.
- Pattern/literal scans and review do not prove the absence of every possible sensitive meaning. Inspect final release members before sharing.

Earlier permitted private field retrospectives remain design context only, outside this distribution. This version's new code and synthetic fixtures were authored independently. It does not redistribute upstream implementation source.

Next evidence: an isolated agent pilot on a low-cost task with fixed tools, permissions, budget and held-out acceptance; compare the old and new instruction versions under the same conditions. Record actual actions, failures, cost and irrelevant work, not just whether the answer sounds reflective.
