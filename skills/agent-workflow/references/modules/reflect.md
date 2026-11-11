# Reflect and retain useful learning

Input: verified results or a rejected plan, previous hypotheses, costs and rival
explanations. Output: `observation`, `counterevidence`, `next_test`, and one
`decision`: continue, pivot, wait, complete or stop. A wait also needs a concrete
`wake_condition`. These fields should change the next action, not recap all logs.

Ask what belief changed, why, and what would overturn the new belief. Distinguish
an implementation error from a valid negative result. Check whether the next
proposal is only a renamed version of an exhausted direction. A plateau prompts
broader hypothesis review; it does not justify random changes or relaxed limits.

Compare the predicted observation with the verified outcome, including actual
cost and unintended regressions. Keep observation separate from explanation.
If a disputed fact controls the next decision, inspect the relevant project
path or retrieve the specific external source using available tools. Reuse
existing evidence; do not start a general literature survey after every result.
The next decision should specify what to retain or change and why. A changed
mechanism opens research; a justified refinement goes to planning and review.
Any new experiment is a separate admitted action, not part of writing reflection.

Use the selective-learning principle from
[Compound Engineering](https://github.com/EveryInc/compound-engineering-plugin):
save a lesson only if losing it would plausibly cause repeated error or material
rediscovery. Prefer a regression check or narrow durable note over another essay.
No new lesson is a valid outcome. Reuse or correct existing notes rather than
accumulating overlapping rules.

The optional runtime `lesson` has `statement`, `why_reusable` and saved `evidence`.
Its current view keeps only eight recent unique statements; the event ledger
retains their provenance. Model-written lessons still need human/domain review
before promotion into shared skills. They must never include private records in
a public package.

For a routine task that passes every acceptance check, finish without requiring
a reflection call or a lesson. In other cases reflect before another attempt.
The engine routes the saved decision in the same transaction: continue → PLAN,
pivot → RESEARCH, or complete/stop/wait. No RESUME callback is needed.
