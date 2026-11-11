"""Software invariants with synthetic artifacts, not an agent-quality benchmark."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

from workflow_runtime import Workflow
from workflow_runtime.demo import contract, envelope, evidence, handlers
from workflow_runtime.local_executor import run_local

ROOT = Path(__file__).resolve().parents[1]


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.workflow = Workflow(self.root, contract())
        self.handlers = handlers()

    def advance(self, count):
        for _ in range(count):
            result = self.workflow.tick(self.handlers)
            self.assertEqual(result["status"], "ready", self.workflow.view())

    def enable(self):
        self.workflow.set_mode("execute", "Explicit synthetic test instruction")

    def test_three_cycles_reopen_database_and_pivot_to_verified_completion(self):
        self.enable()
        for index in range(18):
            self.workflow = Workflow(self.root)
            self.workflow.tick(self.handlers)
        state = self.workflow.view()
        self.assertEqual(state["status"], "done")
        self.assertEqual(state["cycles"], 3)
        self.assertEqual(state["spent"], 3)
        self.assertEqual([a["approach"] for a in state["attempts"]], ["case-only", "case-only", "strip-and-case"])
        self.assertEqual(len(state["lessons"]), 1)

    def test_planning_default_cannot_execute(self):
        self.advance(3)
        self.assertEqual(self.workflow.tick(self.handlers)["status"], "plan_only")
        self.assertEqual(self.workflow.view()["attempts"], [])

    def test_latest_pause_wins_and_stale_graph_route_does_not_advance(self):
        self.enable()
        self.advance(3)
        self.workflow.set_mode("pause", "New user pause")
        self.assertEqual(self.workflow.tick(self.handlers)["status"], "pause")
        self.workflow.set_mode("execute", "User resumed synthetic task")
        self.assertEqual(self.workflow.tick(self.handlers, "PLAN")["status"], "stale_route")
        self.assertEqual(self.workflow.view()["attempts"], [])

    def test_new_planning_scope_overrides_old_execution_scope(self):
        self.enable()
        self.advance(3)
        self.workflow.set_mode("plan_only", "Later plan-only instruction")
        self.assertEqual(self.workflow.tick(self.handlers)["status"], "plan_only")

    def test_contract_cannot_reset_spend_on_reopen(self):
        changed = contract()
        changed["limits"]["max_cost"] *= 2
        with self.assertRaisesRegex(ValueError, "immutable"):
            Workflow(self.root, changed)

    def test_duplicate_wake_during_live_module_does_not_call_it_twice(self):
        entered, release = threading.Event(), threading.Event()
        calls = []
        original = self.handlers["RESEARCH"]
        def slow(state, root):
            calls.append(1)
            entered.set()
            release.wait(3)
            return original(state, root)
        self.handlers["RESEARCH"] = slow
        thread = threading.Thread(target=lambda: self.workflow.tick(self.handlers))
        thread.start()
        self.assertTrue(entered.wait(2))
        try:
            self.assertEqual(Workflow(self.root).tick(self.handlers)["status"], "reconcile_required")
            self.assertEqual(len(calls), 1)
        finally:
            release.set()
            thread.join(3)
        self.assertFalse(thread.is_alive())

    def test_crash_after_effect_is_reconciled_without_second_execution(self):
        self.enable()
        self.advance(3)
        program = '''
import os,sys
from workflow_runtime import Workflow
from workflow_runtime.demo import handlers
w=Workflow(sys.argv[1]); h=handlers(); execute=h["EXECUTE"]
def crash(s,r):
    execute(s,r)
    os._exit(23)
h["EXECUTE"]=crash
w.tick(h)
'''
        process = subprocess.run([sys.executable, "-c", program, str(self.root)], cwd=ROOT, timeout=10)
        self.assertEqual(process.returncode, 23)
        state = self.workflow.view()
        self.assertEqual(self.workflow.tick(self.handlers)["status"], "reconcile_required")
        token = state["inflight"]["token"]
        receipt = json.loads((self.root / (token + ".json")).read_text())
        self.workflow.reconcile(token, envelope(receipt, 1), 0.1)
        self.assertEqual(self.workflow.view()["phase"], "VERIFY")
        self.assertEqual(len(list(self.root.glob("*-labels.json"))), 1)
        with self.assertRaises(ValueError):
            self.workflow.reconcile(token, envelope(receipt, 1), 0.1)
        self.assertEqual(self.workflow.view()["spent"], 1)

    def test_rejected_review_never_launches(self):
        self.enable()
        self.handlers["REVIEW"] = lambda s,r: envelope({"approved": False, "reason": "Not discriminating"})
        self.advance(3)
        self.assertEqual(self.workflow.view()["phase"], "REFLECT")
        self.assertEqual(self.workflow.view()["attempts"], [])

    def test_renaming_candidate_does_not_bypass_duplicate_check(self):
        self.enable()
        self.advance(6)
        original_plan = self.workflow.view()["plan"]
        original_plan["candidate_name"] = "renamed"
        self.handlers["PLAN"] = lambda s,r: envelope(original_plan)
        self.advance(2)
        self.assertEqual(self.workflow.tick(self.handlers)["status"], "blocked")
        self.assertIn("duplicate", self.workflow.view()["blocker"])
        self.assertEqual(len(self.workflow.view()["attempts"]), 1)

    def test_plateau_blocks_more_variants_in_same_direction(self):
        cfg = contract()
        cfg["limits"]["max_family_attempts"] = 5
        self.workflow = Workflow(self.root / "plateau-case", cfg)
        self.enable()
        self.advance(12)
        bad = handlers()["PLAN"](self.workflow.view(), self.root)["data"]
        bad["approach"], bad["change"] = "case-only", "another-variant"
        self.handlers["PLAN"] = lambda s,r: envelope(bad)
        self.advance(2)
        self.workflow.tick(self.handlers)
        self.assertEqual(self.workflow.view()["status"], "blocked")
        self.assertEqual(self.workflow.view()["blocker"], "plateau_requires_different_approach")

    def test_estimated_cost_blocks_launch_without_consuming_an_attempt(self):
        self.enable()
        original = self.handlers["PLAN"]
        def expensive(s,r):
            result = original(s,r)
            result["data"]["estimated_cost"] = 21
            return result
        self.handlers["PLAN"] = expensive
        self.advance(3)
        self.assertEqual(self.workflow.tick(self.handlers)["status"], "blocked")
        self.assertEqual(self.workflow.view()["blocker"], "insufficient_campaign_cost")
        self.assertEqual(self.workflow.view()["attempts"], [])

    def test_cycle_bound_stops_research_after_repeated_replanning(self):
        for _ in range(4):
            self.workflow.replan("Different bounded research question")
        self.assertEqual(self.workflow.tick(self.handlers)["status"], "blocked")
        self.assertEqual(self.workflow.view()["blocker"], "cycle_limit")

    def test_pause_written_during_callback_is_not_lost(self):
        original = self.handlers["RESEARCH"]
        def pause(s,r):
            self.workflow.set_mode("pause", "User changed scope during callback")
            return original(s,r)
        self.handlers["RESEARCH"] = pause
        self.workflow.tick(self.handlers)
        self.assertEqual(self.workflow.view()["mode"], "pause")
        self.assertEqual(self.workflow.tick(self.handlers)["status"], "pause")

    def test_agent_bridge_reads_only_current_module_and_uses_separate_verifier(self):
        from workflow_runtime.agent_bridge import make_agent_handlers
        calls = []
        def reason(request):
            calls.append(request["module"])
            self.assertIn("Do not execute", request["output_contract"])
            self.assertNotIn("workspace", request)
            self.assertLessEqual(len(request["current"]["recent_attempts"]), 4)
            # Scripted provider response: transport/contract test, no LLM efficacy.
            return self.handlers[request["module"]](self.workflow.view(), self.root)
        combined = make_agent_handlers(reason, reason, self.handlers["EXECUTE"], self.handlers["VERIFY"])
        self.enable()
        for _ in range(6):
            self.workflow.tick(combined)
        self.assertEqual(calls, ["RESEARCH", "PLAN", "REVIEW", "REFLECT"])
        self.assertEqual(self.workflow.view()["phase"], "RESEARCH")

    def test_routine_success_uses_only_plan_execute_verify(self):
        self.workflow = Workflow(self.root / "routine", contract("routine"))
        self.enable()
        calls = []
        wrapped = {}
        for phase, handler in self.handlers.items():
            def record(s, r, phase=phase, handler=handler):
                calls.append(phase)
                result = handler(s, r)
                if phase == "PLAN":
                    result["data"].pop("hypothesis")
                    result["data"].pop("falsifier")
                return result
            wrapped[phase] = record
        for _ in range(3):
            self.workflow.tick(wrapped)
        state = self.workflow.view()
        self.assertEqual(calls, ["PLAN", "EXECUTE", "VERIFY"])
        self.assertEqual(state["status"], "done")
        self.assertEqual(state["cycles"], 1)
        self.assertEqual(state["review"]["kind"], "policy_only")
        self.assertEqual(state["lessons"], [])

    def test_routine_still_needs_scope_evidence_and_every_acceptance_check(self):
        self.workflow = Workflow(self.root / "routine", contract("routine"))
        self.workflow.tick(self.handlers)
        self.assertEqual(self.workflow.tick(self.handlers)["status"], "plan_only")
        self.enable()
        self.workflow.tick(self.handlers)
        refs = self.workflow.view()["result"]["evidence"]
        self.handlers["VERIFY"] = lambda s,r: envelope({"valid": True, "improved": True,
            "goal_met": True, "checks": {}, "evidence": refs})
        self.assertEqual(self.workflow.tick(self.handlers)["status"], "reconcile_required")
        self.assertNotEqual(self.workflow.view()["status"], "done")

    def test_routine_pivot_escalates_to_research_and_independent_review(self):
        self.workflow = Workflow(self.root / "routine", contract("routine"))
        self.enable()
        original = self.handlers["PLAN"]
        def wrong(s, r):
            output = original(s, r)
            output["data"]["approach"] = "case-only"
            return output
        self.handlers["PLAN"] = wrong
        self.advance(4)
        self.assertEqual(self.workflow.view()["phase"], "RESEARCH")
        self.advance(2)
        self.assertEqual(self.workflow.view()["phase"], "REVIEW")
        self.assertEqual(len(self.workflow.view()["attempts"]), 1)

    def test_continue_reuses_research_without_a_resume_callback(self):
        self.enable()
        self.advance(5)
        self.handlers["REFLECT"] = lambda s,r: envelope({"decision": "continue",
            "observation": "A bounded follow-up remains", "counterevidence": "Goal not met",
            "next_test": "Test a distinct change with the same research"})
        self.workflow.tick(self.handlers)
        self.assertEqual(self.workflow.view()["phase"], "PLAN")
        self.assertEqual(self.workflow.view()["cycles"], 1)
        self.workflow.tick(self.handlers)
        self.assertEqual(self.workflow.view()["phase"], "REVIEW")

    def test_routine_policy_only_review_cannot_bypass_action_scope(self):
        self.workflow = Workflow(self.root / "routine", contract("routine"))
        original = self.handlers["PLAN"]
        def outside_scope(s, r):
            output = original(s, r)
            output["data"]["action"] = "not_authorized"
            return output
        self.handlers["PLAN"] = outside_scope
        self.assertEqual(self.workflow.tick(self.handlers)["status"], "blocked")
        self.assertEqual(self.workflow.view()["blocker"], "action_outside_recorded_scope")
        self.assertEqual(self.workflow.view()["attempts"], [])

    def test_same_verified_output_needs_six_deliberate_or_three_routine_callbacks(self):
        counts, outputs = [], []
        for effort in ("deliberate", "routine"):
            workflow = Workflow(self.root / effort, contract(effort))
            workflow.set_mode("execute", "Explicit paired synthetic routing test")
            callbacks = handlers()
            original = callbacks["PLAN"]
            def known_plan(s, r):
                result = original(s, r)
                result["data"]["approach"] = "strip-and-case"
                return result
            callbacks["PLAN"] = known_plan
            count = 0
            while workflow.view()["status"] == "ready" and count < 7:
                workflow.tick(callbacks)
                count += 1
            state = workflow.view()
            self.assertEqual(state["status"], "done")
            self.assertTrue(all(state["verification"]["checks"].values()))
            outputs.append(state["verification"]["evidence"][0]["sha256"])
            counts.append(count)
        self.assertEqual(outputs[0], outputs[1])
        self.assertEqual(counts, [6, 3])

    def test_default_effort_still_requires_researched_alternatives(self):
        self.handlers["RESEARCH"] = lambda s,r: envelope({"question": "Known repair", "alternatives": ["one"]})
        self.assertEqual(self.workflow.tick(self.handlers)["status"], "blocked")
        self.assertEqual(self.workflow.view()["attempts"], [])

    def test_old_resume_state_routes_without_a_host_callback(self):
        self.enable()
        self.advance(5)
        with self.workflow.store.transaction() as db:
            state = self.workflow.store.load(db)
            state["phase"] = "RESUME"
            state["reflection"] = {"decision": "pivot"}
            self.workflow.store.save(db, state, "legacy_fixture", {})
        self.workflow.tick({})
        self.assertEqual(self.workflow.view()["phase"], "RESEARCH")
        self.assertEqual(self.workflow.view()["cycles"], 1)

    def test_launch_rechecks_storage_and_preserves_plan(self):
        self.enable()
        self.advance(3)
        (self.root / "filled.txt").write_bytes(b"x" * 4194304)
        self.assertEqual(self.workflow.tick(self.handlers)["status"], "blocked")
        self.assertEqual(self.workflow.view()["attempts"], [])
        self.assertIsNotNone(self.workflow.view()["plan"])

    def test_action_outside_scope_is_rejected(self):
        self.advance(2)
        self.handlers["REVIEW"] = lambda s,r: envelope({"approved": True, "merit": True, "feasibility": True, "acceptance": True, "reason": "check"})
        with self.workflow.store.transaction() as db:
            state = self.workflow.store.load(db)
            state["plan"]["action"] = "unapproved_external_action"
            self.workflow.store.save(db, state, "test_fixture", {})
        self.workflow.tick(self.handlers)
        self.assertEqual(self.workflow.view()["blocker"], "action_outside_recorded_scope")

    def test_unknown_cost_blocks_and_is_not_zeroed(self):
        original = self.handlers["RESEARCH"]
        self.handlers["RESEARCH"] = lambda s,r: dict(original(s,r), cost=None)
        self.assertEqual(self.workflow.tick(self.handlers)["status"], "blocked")
        self.assertTrue(self.workflow.view()["unknown_cost"])
        path = self.root / "usage.json"
        path.write_text('{"cost": 2}')
        self.workflow.resolve_cost(2, [evidence(path, self.root)])
        self.assertEqual(self.workflow.view()["spent"], 2)
        self.assertEqual(self.workflow.view()["phase"], "PLAN")

    def test_saved_result_mutation_blocks_verification(self):
        self.enable()
        self.advance(4)
        ref = self.workflow.view()["result"]["evidence"][0]
        (self.root / ref["path"]).write_text('["tampered"]')
        self.assertEqual(self.workflow.tick(self.handlers)["status"], "reconcile_required")
        self.assertEqual(self.workflow.view()["phase"], "VERIFY")

    def test_false_completion_and_incomplete_checks_are_rejected(self):
        self.enable()
        self.advance(4)
        refs = self.workflow.view()["result"]["evidence"]
        self.handlers["VERIFY"] = lambda s,r: envelope({"valid": True, "improved": False,
            "goal_met": True, "checks": {"exact_labels": False}, "evidence": refs})
        self.assertEqual(self.workflow.tick(self.handlers)["status"], "reconcile_required")
        self.assertNotEqual(self.workflow.view()["status"], "done")

    def test_reflection_must_change_next_decision_not_claim_unverified_goal(self):
        self.enable()
        self.advance(5)
        self.handlers["REFLECT"] = lambda s,r: envelope({"decision": "complete", "observation": "bad claim",
            "counterevidence": "failed check", "next_test": "none"})
        self.assertEqual(self.workflow.tick(self.handlers)["status"], "blocked")

    def test_stopped_task_does_not_reopen(self):
        self.workflow.set_mode("stop", "User stopped this task")
        with self.assertRaises(ValueError):
            self.enable()
        self.assertEqual(self.workflow.tick(self.handlers)["status"], "stop")

    @unittest.skipUnless(os.name == "posix", "POSIX process group adapter")
    def test_local_executor_timeout_saves_failed_receipt_and_reuses_it(self):
        token = "a" * 32
        receipt = run_local([sys.executable, "-c", "import time; time.sleep(5)"], self.root, token, 0.1)
        self.assertEqual(receipt["reason"], "timeout")
        self.assertEqual(receipt["status"], "failed")
        self.assertLess(receipt["elapsed_seconds"], 2)
        self.assertEqual(run_local([sys.executable, "-c", "import time; time.sleep(5)"], self.root, token, 0.1), receipt)
        with self.assertRaisesRegex(ValueError, "different_command"):
            run_local(["unused"], self.root, token, 0.1)

    @unittest.skipUnless(os.name == "posix", "POSIX process group adapter")
    def test_local_executor_caps_retained_logs(self):
        receipt = run_local([sys.executable, "-c", "print('x'*100000)"], self.root, "b"*32, 2, 1024)
        self.assertTrue(receipt["logs_truncated"])
        self.assertEqual(receipt["reason"], "output_limit")
        self.assertEqual(sum((self.root/r["path"]).stat().st_size for r in receipt["evidence"]), 1024)


if __name__ == "__main__":
    unittest.main()
