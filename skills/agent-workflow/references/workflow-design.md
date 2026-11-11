# Designing a research or improvement task

An executable task contract answers: what outcome is wanted, how completion is checked, what actions are permitted, what limits and stop conditions apply, which source reports execution/results, and what happens after a milestone, failure, or interruption.

Separate attempt completion from goal completion. A cleanly executed negative experiment may not achieve its research objective; a produced export may fail completeness checks; passing local tests may not authorize deployment.

A single research-and-improvement cycle does not require a scheduler. Start from
the question and the evidence needed for a decision; add persistent continuation
when the work spans sessions or waits on an external job.

## Choose the evidence before the action

- For project behavior, inspect the relevant implementation, callers,
  configuration, tests and already saved measurements. Scope the search to the
  question rather than scanning the entire project or data store.
- For a method, API or prior finding, use available documentation, web or
  scholarly search. Prefer a primary source that exposes the relevant assumption
  or interface, and retain its version and exact location.
- For adaptation, map external requirements to the actual project. Record both
  matches and mismatches; finding a successful paper is not a local diagnosis.

Planning and review can fill a specific evidence gap without restarting the
entire research stage. Stop retrieval once it can support a reviewable choice,
or record what remains unknown when its bound is reached. Search queries should
describe the general technical question, not disclose private project material.

## Reflection that changes a decision

Write evidence → explanation → counterevidence/unknown → decision. A decision may retain a result, reject a hypothesis, repair a bug, gather a specific missing fact, or execute a ready action. Do not require literature search, TDD, multiple agents, or a long report for every domain.

Ask which observation would change the decision. Prefer the cheapest relevant check. With no new evidence, stop that branch, name a wake condition, or select a distinct justified action. More reflection text is not independent evidence.

## Examples

| Domain | Observe and verify | Reflect and plan | Execute and finish |
|---|---|---|---|
| Software regression | Selected issue, commit, CI/native job, and actual reproduction; reconcile active runs | Product fault versus flaky infrastructure; smallest supported fix and relevant check | Modify authorized scope, verify, and prepare requested deliverable; publish/deploy only if authorized |
| Method exploration | Primary method assumptions, local implementation and a fixed baseline | Mechanism and rival explanation; exploratory test versus confirmation | Review the design, run the bounded comparison, and retain supported conclusions and limits |
| Model improvement | Actual training status, saved milestones, fixed input/config identities and evaluation | Software fault versus valid negative result versus resource infeasibility; falsifiable next change | Proportionate scientific/engineering checks before expensive runs; evaluate agreed final artifact without picking a favorable intermediate afterward |
| Learning | Learner's current demonstration and a reliable reference or worked example | Misconception versus unfamiliarity; smallest useful exercise | Attempt the exercise, check independently, and adjust the next practice from observed errors |
| Large dataset | Partition jobs, manifests, checksums, counts and reconciliation | Missing partition never launched, failed, or completed without receipt? | Resume proven missing work under stable partition/idempotency key; check totals, duplicates and outputs |

These are examples, not permissions or universal defaults. Read-only monitoring needs no mutation; one-time work may need no scheduler.

## Synthetic walkthrough: batch-processing optimization

This illustrates decisions, not a benchmark result or a supplied project.
Suppose a text-processing project may repeatedly parse an unchanged schema.
The goal is less processing time with identical output and error behavior.

1. **Investigate.** Inspect the actual entry point and schema caller, relevant
   tests and saved timings. Check the parser's official documentation only if
   its reuse or mutability rules are unclear. Save source locations and gaps.
   A repeated call suggests a hypothesis; it does not prove the bottleneck.
2. **Plan.** If baseline evidence is missing, first propose a bounded baseline
   measurement. With a usable baseline, propose reusing the parsed schema as
   one change. Keep inputs, ordering, concurrency and comparison conditions
   fixed; declare correctness and time/memory checks before execution.
3. **Review.** Check schema lifetime and mutability, whether failures still
   surface correctly, comparison validity and the whole resource estimate.
   If safety is unknown, narrow to an isolated test instead of changing the
   production path. A new baseline or pilot is reviewed as its own action.
4. **Execute.** Make only the admitted local change and run the agreed checks.
   Retain code/input identities, outputs, timings, failures and actual usage.
5. **Verify.** Check output content and order, error cases and the agreed
   performance comparison. Explain cache/run-order effects and inconclusive
   measurements; do not report improvement from the fastest run alone.
6. **Reflect.** Compare the result with the hypothesis. If correctness holds
   but there is no useful gain, retain that negative evidence. Inspect another
   plausible cost only when it could change the decision; do not keep renaming
   cache variants. A supported refinement returns to planning, a different
   mechanism returns to research, and accepted work completes.

No network access is needed if the local evidence and existing documentation
answer the question. No reflection needs to repeat a completed search.

Before trusting unattended operation, demonstrate on disposable work that duplicate wakeups do not relaunch a job, pause is respected, negative results are not called success, and interruption reconciles an ambiguous launch. Test actual runtime enforcement separately from instructions. Begin with low-cost work within explicit scope.
