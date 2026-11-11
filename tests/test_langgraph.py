"""Optional actual LangGraph integration, no model calls or tracing service."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

from workflow_runtime import Workflow
from workflow_runtime.demo import contract, handlers


@unittest.skipUnless(importlib.util.find_spec("langgraph"), "Install optional LangGraph requirements")
class GraphTests(unittest.TestCase):
    def test_bounded_graph_wakes_resume_from_durable_stage(self):
        from workflow_runtime.langgraph_adapter import build_graph
        with tempfile.TemporaryDirectory() as directory:
            for _ in range(3):
                workflow = Workflow(Path(directory), contract())
                if workflow.view()["revision"] == 1:
                    workflow.set_mode("execute", "Explicit synthetic graph test")
                graph = build_graph(workflow, handlers(), max_steps=6)
                graph.invoke({"steps": 0, "result": {}}, {"recursion_limit": 15})
            self.assertEqual(workflow.view()["status"], "done")
            self.assertEqual(len(workflow.view()["attempts"]), 3)

    def test_graph_yields_on_plan_only_without_spinning(self):
        from workflow_runtime.langgraph_adapter import build_graph
        with tempfile.TemporaryDirectory() as directory:
            workflow = Workflow(Path(directory), contract())
            result = build_graph(workflow, handlers()).invoke({"steps": 0, "result": {}})
            self.assertEqual(result["steps"], 4)
            self.assertEqual(result["result"]["status"], "plan_only")
            self.assertEqual(workflow.view()["attempts"], [])

    def test_graph_routine_success_runs_three_nodes_without_review_or_reflection(self):
        from workflow_runtime.langgraph_adapter import build_graph
        with tempfile.TemporaryDirectory() as directory:
            workflow = Workflow(Path(directory), contract("routine"))
            workflow.set_mode("execute", "Explicit routine synthetic test")
            result = build_graph(workflow, handlers()).invoke({"steps": 0, "result": {}})
            self.assertEqual(result["steps"], 3)
            self.assertEqual(workflow.view()["status"], "done")
