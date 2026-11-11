Use $agent-workflow to continue the explicitly selected task at `<task-directory>/workflow.json` and `<task-directory>/state.json`.

Read live state, controls, authorization/limits, and the active attempt's actual executor status. Resume the unfinished step. Preserve failures, evidence, and usage. Reconcile ambiguous launches or external effects before retrying. Continue already-authorized work once preconditions are met. Do not repeat completed expensive work merely to refresh a status report.

Notify only on meaningful results, failures, recovery, changed decisions, or needed user action, unless routine updates were explicitly requested. Otherwise use the host's quiet-response convention. Save the next action or wake condition. Finishing an attempt does not itself finish the goal or delete its monitor.
