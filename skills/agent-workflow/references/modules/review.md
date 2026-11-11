# Review the plan

Input: the exact proposed plan and current scope/resources. Output: an admitted
plan identity or a rejection with the specific gap. Separate:

- Merit: does the action answer a useful question, and what rival explanation remains?
- Feasibility: can the real path run within the original limits, including overhead?
- Acceptance: are checks independent, complete, and bound to the same inputs and outputs?

For research and optimization, make these judgments concrete:

- Trace the key claim to source evidence and check that its assumptions hold in
  the actual project. Popularity or a paper's reported gain is not local proof.
- Check the baseline, changed variables, comparable inputs, measurement method
  and important confounders. The planned observation must be capable of
  disproving the hypothesis. Protect held-out evaluation when applicable.
- Distinguish a bounded exploratory test from confirmation. Limited evidence can
  justify testing an uncertain idea; it cannot justify calling that idea proven.
- Check the whole execution and verification path, including startup, storage,
  failure handling and available tools. Scientific merit alone is not readiness.

Use targeted project inspection or external retrieval to check a disputed fact.
If it remains decisive and unresolved, reject with the exact missing evidence
and the smallest useful way to obtain it. Do not execute the plan to fill a
review gap. Revise first, then review the revised plan before launch; an old
approval does not cover changed actions, inputs or acceptance rules.

The runtime callback supplies `approved`, `merit`, `feasibility`, `acceptance`
and `reason`. The engine also checks scope, duplicates, approach limits, remaining
resources and the plan digest. Boolean flags are records of a review, not proof
that it was performed correctly. Use domain-specific checks where needed.

Do not repeat the same review without changed evidence. Reject or narrow an
unjustified expensive action. A planning-only user request permits preparing the
review; it does not permit launching the action. Recheck launch preconditions
immediately before execution because storage, controls and workers can change.

The explicitly routine route folds deterministic checks into PLAN; it does not
call this independent reviewer or claim a scientific-merit verdict. Unknown or
expensive work belongs on the deliberate route.
