#!/usr/bin/env python3
"""Run one bounded wake of a synthetic workflow; no APIs, models, or datasets."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workflow_runtime import Workflow
from workflow_runtime.demo import contract, handlers


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True, help="Private runtime directory outside the public kit")
    parser.add_argument("--steps", type=int, default=6)
    parser.add_argument("--effort", choices=("routine", "deliberate"), default="deliberate")
    parser.add_argument("--langgraph", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.steps <= 100:
        parser.error("--steps must be between 1 and 100")
    root = Path(__file__).resolve().parents[1]
    if args.workspace.resolve().is_relative_to(root):
        parser.error("Keep generated run data outside the public kit")
    workflow = Workflow(args.workspace, contract(args.effort))
    if workflow.view()["revision"] == 1:
        workflow.set_mode("execute", "User explicitly invoked the synthetic local demo")
    if args.langgraph:
        from workflow_runtime.langgraph_adapter import build_graph
        build_graph(workflow, handlers(), args.steps).invoke({"steps": 0, "result": {}},
                                                         {"recursion_limit": args.steps + 5})
    else:
        for _ in range(args.steps):
            if workflow.tick(handlers())["status"] != "ready":
                break
    state = workflow.view()
    print(json.dumps({key: state[key] for key in ("phase", "status", "revision", "cycles", "spent", "plateau")}, indent=2))


if __name__ == "__main__":
    main()
