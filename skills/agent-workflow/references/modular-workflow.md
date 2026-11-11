# Research and improvement modules

Use only the module for the current unfinished stage. These are logical modules,
not mandatory separate agents. The same host may implement the needed work. A module
may call a relevant installed domain skill, but this kit does not install or
execute third-party skills automatically.

Capability discovery and workflow improvement happen inside the relevant
research, plan or reflection module, not as another mandatory stage. Use
[skill evolution](skill-evolution.md) for a concrete gap or verified workflow
defect; keep normal task execution on its current tested revision.

The minimal route is **plan → execute → verify** for a known cheap reversible
action. Use **research → plan → review → execute → verify → reflect** for uncertain
or consequential work. Research and reflection are conditional, not forms to fill
at every wake. See [parameters](parameters.md) for the runtime effort choice.
Continuation is deterministic routing from saved decisions, not another agent.
One cycle is useful without a scheduler; the same records support ongoing work.

| Module | Input → durable output | Read when |
|---|---|---|
| [Research / learn](modules/research.md) | decision-relevant question + evidence → competing approaches | A new action needs justification |
| [Plan](modules/plan.md) | chosen approach → falsifiable action and cost estimate | Preparing the next attempt |
| [Review](modules/review.md) | exact plan → merit, feasibility and acceptance verdict | Before committing resources |
| [Execute](modules/execute.md) | admitted plan → native receipt, logs and actual usage | Work is authorized and ready |
| [Verify](modules/verify.md) | receipt + immutable outputs → acceptance results | Execution ended |
| [Reflect](modules/reflect.md) | verified result or rejected plan → changed decision and optional lesson | Evidence can change the next action |
| [Resume](modules/resume.md) | current scope + durable phase → next module or named wait | Every wake or session handoff; routing, not a model call |

## Investigation throughout the loop

RESEARCH frames the question and alternatives. PLAN may still inspect a caller,
test or official API detail; REVIEW may check an assumption against its source;
REFLECT may retrieve a missing fact that distinguishes rival explanations.
These are targeted read-only tool calls inside the current module, not mandatory
new stages. A fundamentally different question or approach reopens RESEARCH.

Use local evidence for actual project behavior and external primary sources for
methods or interfaces. Save source/version/location, observation, supported
claim and limits, optionally as `basis` records. Connect the two when adapting a
method; resemblance alone does not establish compatibility or local benefit.
Do not send private project material to search or other external tools without
authorization. Use relevant available domain skills, without making them a
required installation or inventing unavailable tools.

Review before execution asks whether the hypothesis is worth testing, the
comparison can answer it and the whole path is feasible. Verification after
execution asks what the saved result actually establishes. Both are needed for
uncertain research; a review pass is not a result. Reflection compares the result
with the prediction and chooses a concrete next action. A diagnostic or pilot
that executes code is an admitted action, not a hidden research tool call.

## Thinking that changes decisions

Before costly work, consider a credible alternative and an explanation under
which the preferred idea fails. Do not perform two complete studies merely to
fill an alternatives field. Reuse earlier evidence while its identity and scope
remain applicable. Spend more review effort on uncertain, expensive actions;
use a short check for reversible routine work.

Give exploration a stopping rule: the question to answer, the observation that
would change the decision, a time/cost bound, and the action after either answer.
When no affordable check can distinguish the alternatives, report that boundary
and choose a different useful question or wait. More prose is not more evidence.

## Avoiding a narrow search loop

Record approach family, actual change, inputs and evaluation identity separately
from display name. A renamed attempt is still the same experiment. After the
task's chosen plateau window, revisit assumptions or select a different approach
instead of adding another tiny variation. Never use held-out final results to
tune the next action when the task requires a protected final evaluation.

Keep software failures, invalid comparisons and valid negative results distinct.
Do not discard a useful negative result or claim an effect from one observation.
These practices reduce known repetition; neither they nor a state machine can
guarantee a global optimum or good scientific judgment.

## Files, memory and resources

Use one authoritative task state with a compact current projection. Store large
outputs separately and refer to their identities, rather than embedding parent
histories. Capture only lessons that would prevent material rediscovery; update
an existing lesson when it becomes wrong. Do not automatically edit the global
skill from an unverified result.

Before launching, compare estimated total work and storage against remaining
campaign resources. Record failed work and unknown costs. Prefer a completion
event to frequent polling; use bounded polling for missed events. Each wake
should execute a relevant module, leave an existing job alone, or yield for a
named condition. Never delete evidence to make room automatically. Archive or
remove regenerable outputs only under an explicit retention policy.

## Implementations

The optional repository runtime (see `docs/runtime.zh-CN.md` in the full kit)
implements these conditional routes with one SQLite authority and an optional
LangGraph router. Existing task systems should bind these module contracts to their own source of truth,
not install a second controller. The file templates remain useful without Python.

The ideas of persistent plans are informed by
[Planning with Files](https://github.com/OthmanAdi/planning-with-files), and selective
durable lessons by [Compound Engineering](https://github.com/EveryInc/compound-engineering-plugin).
This implementation is original; it does not vendor their code or require them.
