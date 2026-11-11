"""Proportional reasoning with durable claims and uncertain-effect recovery."""
import copy
import time
import uuid

from .policy import PHASES, check_evidence, check_plan, check_resources, digest, fingerprint, number
from .store import Store, encode


class Workflow:
    def __init__(self, directory, contract=None):
        self.store = Store(directory)
        with self.store.transaction() as db:
            current = self.store.load(db)
            if current:
                if contract is not None and digest(contract) != digest(current["contract"]):
                    raise ValueError("existing_contract_is_immutable")
                return
            if contract is None:
                raise ValueError("new_task_requires_contract")
            required = ("max_cycles", "max_family_attempts", "plateau_patience", "max_cost",
                        "max_seconds", "min_free_bytes", "max_workspace_bytes", "max_workspace_files")
            limits = contract.get("limits", {})
            if any(not number(limits.get(key)) or limits[key] <= 0 for key in required):
                raise ValueError("positive_explicit_limits_required")
            if any(not isinstance(limits[key], int) for key in
                   ("max_cycles", "max_family_attempts", "plateau_patience", "max_workspace_files")):
                raise ValueError("integer_count_limits_required")
            if not contract.get("task_id") or not contract.get("goal") or not contract.get("acceptance"):
                raise ValueError("task_goal_and_acceptance_required")
            if contract.get("effort", "deliberate") not in ("routine", "deliberate"):
                raise ValueError("effort_must_be_routine_or_deliberate")
            phase = "PLAN" if contract.get("effort") == "routine" else "RESEARCH"
            state = {"contract": contract, "revision": 0, "phase": phase, "status": "ready",
                     "mode": "plan_only", "mode_source": None, "inflight": None,
                     "cycles": 0, "spent": 0, "seconds": 0, "unknown_cost": False,
                     "plateau": 0, "attempts": [], "lessons": [], "research": None,
                     "plan": None, "review": None, "result": None, "verification": None,
                     "reflection": None, "blocker": None, "wake_condition": None}
            self.store.save(db, state, "created", {"task_id": contract["task_id"]})

    def view(self):
        return self.store.read()

    def set_mode(self, mode, source):
        """Called by the trusted host for a real user instruction, never by log text."""
        if mode not in ("execute", "plan_only", "pause", "stop") or not source:
            raise ValueError("explicit_mode_and_source_required")
        with self.store.transaction() as db:
            state = self.store.load(db)
            if state["mode"] == "stop" or state["status"] in ("done", "stopped"):
                raise ValueError("terminal_task_cannot_be_reopened")
            state["mode"], state["mode_source"] = mode, source
            self.store.save(db, state, "scope_changed", {"mode": mode, "source": source})

    def unblock(self, reason):
        """Acknowledges a repaired non-execution precondition; never clears an intent."""
        if not reason:
            raise ValueError("unblock_reason_required")
        with self.store.transaction() as db:
            state = self.store.load(db)
            if state["inflight"] or state["unknown_cost"] or state["status"] in ("done", "stopped"):
                raise ValueError("reconciliation_or_terminal_state")
            state["status"], state["blocker"], state["wake_condition"] = "ready", None, None
            self.store.save(db, state, "unblocked", {"reason": reason})

    def replan(self, reason):
        """Reopen research without resetting costs, attempts, or plateau history."""
        if not reason:
            raise ValueError("new_research_question_required")
        with self.store.transaction() as db:
            state = self.store.load(db)
            if state["inflight"] or state["unknown_cost"] or state["status"] in ("done", "stopped"):
                raise ValueError("reconcile_or_finish_current_work_first")
            if state["phase"] in ("VERIFY", "REFLECT", "RESUME"):
                raise ValueError("finish_result_review_before_replanning")
            state["phase"], state["status"], state["blocker"] = "RESEARCH", "ready", None
            state["cycles"] += 1
            self.store.save(db, state, "replanned", {"reason": reason})

    def tick(self, handlers, expected_phase=None):
        """Runs at most one module. Duplicate wakes never reclaim an unfinished claim."""
        with self.store.transaction() as db:
            state = self.store.load(db)
            if state["inflight"]:
                return {"status": "reconcile_required", "phase": state["phase"]}
            if state["mode"] in ("pause", "stop"):
                return {"status": state["mode"], "phase": state["phase"]}
            if state["status"] != "ready":
                return {"status": state["status"], "phase": state["phase"]}
            phase = state["phase"]
            if expected_phase is not None and expected_phase != phase:
                return {"status": "stale_route", "phase": phase}
            if phase == "EXECUTE" and state["mode"] != "execute":
                return {"status": "plan_only", "phase": phase}
            try:
                if phase in ("RESEARCH", "PLAN", "REVIEW", "EXECUTE"):
                    check_resources(state, self.store.directory, phase == "EXECUTE")
                if phase == "EXECUTE":
                    check_plan(state)
                    if state["review"]["plan_digest"] != digest(state["plan"]):
                        raise ValueError("plan_changed_after_review")
                # Old databases may end on RESUME. Routing is engine work,
                # never a reason to call an agent or a host callback.
                handler = (lambda s, r: {"data": {"next": self._next(s)}, "cost": 0}) if phase == "RESUME" else handlers[phase]
            except (ValueError, KeyError) as error:
                state["status"], state["blocker"] = "blocked", str(error)
                self.store.save(db, state, "precondition_blocked", {"phase": phase, "reason": str(error)})
                return {"status": "blocked", "phase": phase, "reason": str(error)}
            token = uuid.uuid4().hex
            state["inflight"] = {"token": token, "phase": phase, "at": time.time()}
            if phase == "EXECUTE":
                state["attempts"].append({"id": token, "fingerprint": fingerprint(state["plan"]),
                                          "approach": state["plan"]["approach"], "status": "intent"})
            self.store.save(db, state, "module_claimed", state["inflight"])
            snapshot = copy.deepcopy(state)
        start = time.monotonic()
        try:
            output = handler(snapshot, self.store.directory)
            self._finish(token, output, time.monotonic() - start)
        except Exception as error:
            with self.store.transaction() as db:
                state = self.store.load(db)
                if state["inflight"] and state["inflight"]["token"] == token:
                    state["inflight"]["observed_seconds"] = time.monotonic() - start
                    state["status"] = "reconcile_required"
                    state["blocker"] = type(error).__name__ + ": " + str(error)[:500]
                    self.store.save(db, state, "module_interrupted", {"phase": phase, "error": state["blocker"],
                        "observed_seconds": state["inflight"]["observed_seconds"], "cost": None})
            return {"status": "reconcile_required", "phase": phase}
        state = self.view()
        return {"status": state["status"], "phase": state["phase"]}

    def reconcile(self, token, output, elapsed_seconds):
        """Host supplies an identity-bound receipt after checking the old worker ended.

        Never call this merely because a lease/PID is absent. For EXECUTE the
        receipt must identify the same idempotency key, including failed jobs.
        """
        self._finish(token, output, elapsed_seconds, recovered=True)

    def _finish(self, token, output, elapsed_seconds, recovered=False):
        if not isinstance(output, dict) or len(encode(output).encode()) > 32768:
            raise ValueError("module_output_must_be_a_bounded_object")
        if not number(elapsed_seconds):
            raise ValueError("actual_elapsed_required_for_reconciliation")
        if "cost" not in output or (output["cost"] is not None and not number(output["cost"])):
            raise ValueError("actual_cost_or_explicit_null_required")
        with self.store.transaction() as db:
            state = self.store.load(db)
            claim = state["inflight"]
            if not claim or claim["token"] != token:
                raise ValueError("claim_already_committed_or_wrong_token")
            if elapsed_seconds < claim.get("observed_seconds", 0):
                raise ValueError("reconciled_time_cannot_erase_observed_time")
            phase = claim["phase"]
            data = output["data"]
            # Validate before clearing intent, so malformed receipts need reconciliation.
            if phase == "EXECUTE":
                if data.get("attempt_id") != token or data.get("status") not in ("completed", "failed"):
                    raise ValueError("execution_receipt_identity_or_status")
                check_evidence(data.get("evidence"), self.store.directory)
            if phase == "VERIFY":
                check_evidence(state["result"]["evidence"], self.store.directory)
                check_evidence(data.get("evidence"), self.store.directory)
                checks = data.get("checks", {})
                if set(checks) != set(state["contract"]["acceptance"]) or any(type(v) is not bool for v in checks.values()):
                    raise ValueError("verification_must_cover_every_acceptance_check")
                if any(type(data.get(key)) is not bool for key in ("valid", "improved", "goal_met")):
                    raise ValueError("explicit_verification_booleans_required")
                if data["goal_met"] and (not data["valid"] or not all(checks.values()) or state["result"]["status"] != "completed"):
                    raise ValueError("goal_claim_without_complete_valid_evidence")
                if data["improved"] and not data["valid"]:
                    raise ValueError("invalid_result_cannot_count_as_improvement")
            state["seconds"] += elapsed_seconds
            state["spent"] += output["cost"] if output["cost"] is not None else 0
            state["unknown_cost"] = output["cost"] is None
            state["inflight"], state["status"], state["blocker"] = None, "ready", None
            try:
                self._apply(state, phase, data)
            except (ValueError, KeyError, TypeError) as error:
                state["status"], state["blocker"] = "blocked", str(error)
            if state["unknown_cost"]:
                state["status_before_cost_block"] = state["status"]
                state["blocker_before_cost_block"] = state["blocker"]
                state["status"], state["blocker"] = "blocked", "unknown_cost_requires_reconciliation"
            self.store.save(db, state, "module_reconciled" if recovered else "module_completed",
                            {"phase": phase, "token": token, "output": output, "elapsed_seconds": elapsed_seconds})

    def resolve_cost(self, cost, evidence):
        if not number(cost):
            raise ValueError("actual_cost_required")
        check_evidence(evidence, self.store.directory)
        with self.store.transaction() as db:
            state = self.store.load(db)
            if not state["unknown_cost"] or state["inflight"]:
                raise ValueError("no_completed_unpriced_module")
            state["spent"] += cost
            state["unknown_cost"] = False
            state["status"] = state.pop("status_before_cost_block", "ready")
            state["blocker"] = state.pop("blocker_before_cost_block", None)
            self.store.save(db, state, "cost_reconciled", {"cost": cost, "evidence": evidence})

    def _apply(self, state, phase, data):
        if phase == "RESEARCH":
            if not data.get("question") or len(set(data.get("alternatives", []))) < 2:
                raise ValueError("research_needs_question_and_distinct_alternatives")
            state["research"], state["phase"] = data, "PLAN"
        elif phase == "PLAN":
            state["plan"], state["result"], state["verification"] = data, None, None
            state["review"], state["reflection"] = None, None
            if state["contract"].get("effort") == "routine" and state["research"] is None:
                check_plan(state)
                state["review"] = {"kind": "policy_only", "plan_digest": digest(data)}
                state["phase"] = "EXECUTE"
            else:
                state["phase"] = "REVIEW"
        elif phase == "REVIEW":
            if data.get("approved") is not True:
                state["review"], state["phase"] = data, "REFLECT"
                return
            if not data.get("reason") or any(data.get(key) is not True for key in ("merit", "feasibility", "acceptance")):
                raise ValueError("review_needs_merit_feasibility_and_acceptance")
            check_plan(state)
            state["review"] = dict(data, plan_digest=digest(state["plan"]))
            state["phase"] = "EXECUTE"
        elif phase == "EXECUTE":
            state["result"], state["phase"] = data, "VERIFY"
            state["attempts"][-1]["status"] = data["status"]
        elif phase == "VERIFY":
            state["verification"], state["phase"] = data, "REFLECT"
            state["attempts"][-1]["improved"] = data["improved"]
            state["plateau"] = 0 if data["improved"] else state["plateau"] + 1
            if state["contract"].get("effort") == "routine" and data["goal_met"]:
                state["phase"], state["status"] = "VERIFY", "done"
                state["cycles"] += 1
        elif phase == "REFLECT":
            if data.get("decision") not in ("continue", "pivot", "wait", "complete", "stop"):
                raise ValueError("reflection_decision_required")
            for key in ("observation", "counterevidence", "next_test"):
                if not data.get(key):
                    raise ValueError("reflection_missing_" + key)
            if data["decision"] == "complete" and not (state["verification"] or {}).get("goal_met"):
                raise ValueError("completion_requires_verified_goal")
            if data["decision"] == "wait" and not data.get("wake_condition"):
                raise ValueError("waiting_needs_wake_condition")
            lesson = data.get("lesson")
            if lesson:
                if not state["verification"] or not lesson.get("statement") or not lesson.get("why_reusable"):
                    raise ValueError("lesson_needs_verified_result_and_reuse_reason")
                check_evidence(lesson.get("evidence"), self.store.directory)
                if not any(item["statement"] == lesson["statement"] for item in state["lessons"]):
                    state["lessons"] = (state["lessons"] + [lesson])[-8:]
            state["reflection"] = data
            self._resume(state)
        elif phase == "RESUME":
            if data.get("next") != self._next(state):
                raise ValueError("resume_must_follow_verified_decision")
            self._resume(state)

    @staticmethod
    def _next(state):
        decision = state["reflection"]["decision"]
        return {"complete": "DONE", "stop": "STOP", "wait": "WAIT", "continue": "PLAN"}.get(decision, "RESEARCH")

    def _resume(self, state):
        next_phase = self._next(state)
        state["cycles"] += 1
        if next_phase in ("DONE", "STOP"):
            state["status"] = "done" if next_phase == "DONE" else "stopped"
        elif next_phase == "WAIT":
            state["status"], state["wake_condition"] = "waiting", state["reflection"]["wake_condition"]
        else:
            state["phase"] = next_phase
