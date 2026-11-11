# Evaluating agent behavior

This directory is a **test specification**, not a completed benchmark or an executable evaluation harness. All 34 cases are currently unrun: 27 behavior cases and 7 activation cases. Software tests in `tests/` inspect the package and synthetic reference runtime; they do not produce agent behavior scores. See [validation status](validation.md).

## Inputs and grading

- [prompts.json](prompts.json): requests, entrypoint, and optional context/fixture; give only the selected case to the actor.
- [fixtures/](fixtures/running.json): synthetic starting records. These are small observations, not a process supervisor or live executor.
- [rubric.json](rubric.json): desired outcomes and critical failures; reserve this file for the grader.
- [result-template.json](result-template.json): record real results, trace identity, time, tokens, and cost. Unknown remains null; do not fill scores from this documentation.

Before execution, materialize each case into a disposable task workspace with actual editable files and available tools. Several cases currently provide only a scenario description and need concrete artifacts. For example, `ready-authorized` needs a selected reversible plan, real working lock, and permission scoped to the sample workspace; `small-action` needs a draft containing the typo. A fixture's statement that a lock exists does not implement a lock. Describe what the runner really enforces.

The investigation cases need a small project and versioned source material
served by controlled search/read tools. Record queries and reads, outbound
payloads, plan revisions and execution order. A prose claim that sources were
checked does not demonstrate retrieval, privacy preservation or pre-execution
review. Offline source fixtures test evidence use, not live web availability.

For process/launch cases, expose controlled executor tools with recorded job identity and an action log. To test real interruption recovery, use an actual cheap sample process and interrupt between launch and receipt. A canned JSON status tests decision-making under that observation only. It does not test the executor's durability or locking.

Keep the actor's accessible workspace free of the rubric, expected answers, other runs, and the author's analysis. Do not point it at this whole repository. Copy only the exact skill version and the selected raw artifacts. Prompts that explicitly state the hazard are useful smoke cases; add held-out variants where the agent must discover the conflict in evidence before claiming generalization.

The capability/evolution cases need controlled discovery and source reads, editable
synthetic candidate skill copies, revision-bound active-attempt records and
action-based old/new evaluators. Materialize the supplied scenarios and log
queries, candidate selection, edits, evaluation and adoption order. A record
claiming an active revision is not a live hot-swap test; report that limitation.

## Preserve the real entrypoint

For **behavior** tests, explicitly load the intended skill bytes and provide the selected request. For **activation** tests, expose the skill through the host's normal discovery mechanism without naming it in the request; record the host's selection trace. An explicitly invoked skill cannot establish discovery accuracy. The seven activation cases are a starter set, not enough to optimize a description reliably.

A scheduled case should use the host's actual scheduled/standing-instruction framing. Do not simply prefix a direct user request with “scheduled” and claim equivalent coverage. When only simulated entrypoints are available, record that limitation. Keep the unchanged scheduled-check case separate from the direct status question: silence appropriate for a monitor must not suppress an answer to a user.

## Compare versions fairly

Use the same case, model, host, tools, permissions, and resource limits in fresh isolated sessions. Inject exact old/new skill bytes, or compare with and without the skill. Record hashes and configuration; do not accidentally test a cached installed version. Randomize arm order where practical and blind the reviewer to version labels.

Inspect actual actions and outputs, not whether the answer mentions the right words. Grade task success, critical failures, overreach, missing requested work, repeated permission requests, duplicate execution, and cost separately. A critical failure cannot be hidden by averaging many easy passes. Count time/tokens only when measured, and retain failures and partial runs. An identical pass in both arms demonstrates neither a gain nor an informative fixture.

Start with a small paired pilot, then repeat discriminating cases at least three times per arm before drawing a directional conclusion. Report denominators, per-case outcomes, variance, and untested conditions. Separate new held-out cases from those used to revise the skill. Human review should explain why outcomes differ and whether a tool stub concealed the behavior being changed.

## Report boundaries

Use the result template once per real case/arm/repetition, with trace and artifact references. Store private execution traces outside the public package; share only reviewed synthetic reproductions. Record a host lacking a capability as such, rather than pretending a scheduler or external write happened.

Do not use live user jobs, paid compute, production data, or real external side effects for this starter suite. Any later runtime integration needs its own authorized test plan. No commands in the release script execute these evaluations or enable monitoring.
