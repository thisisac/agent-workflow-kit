"""Synthetic local example: improve a text transformation, then pivot approach."""
import hashlib
import json


def contract(effort="deliberate"):
    return {"task_id": "synthetic-text-task", "goal": "Normalize three synthetic labels",
            "acceptance": ["exact_labels"], "effort": effort,
            "authorization": {"source": "Explicit local synthetic-demo invocation",
                              "allowed_actions": ["normalize_synthetic_labels"]},
            "limits": {"max_cycles": 4, "max_family_attempts": 2, "plateau_patience": 2,
                       "max_cost": 20, "max_seconds": 30, "min_free_bytes": 1048576,
                       "max_workspace_bytes": 4194304, "max_workspace_files": 100}}


def evidence(path, root):
    return {"path": path.relative_to(root).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def envelope(data, cost=0):
    return {"data": data, "cost": cost}


def handlers():
    def research(state, root):
        return envelope({"question": "Which transformation handles whitespace and case?",
                         "alternatives": ["case-only", "strip-and-case"],
                         "uncertainty": "Case conversion alone may retain leading spaces."})

    def plan(state, root):
        attempts = len(state["attempts"])
        approach = "case-only" if attempts < 2 and state["contract"].get("effort") != "routine" else "strip-and-case"
        return envelope({"approach": approach, "change": "variant-" + str(attempts),
                         "inputs": "synthetic-labels-v1", "evaluation": "exact-label-match-v1",
                         "hypothesis": "Whitespace handling may be needed in addition to case.",
                         "falsifier": "Any normalized label differs from the frozen expected list.",
                         "action": "normalize_synthetic_labels", "estimated_cost": 1,
                         "estimated_seconds": 0.1, "estimated_bytes": 4096})

    def review(state, root):
        return envelope({"approved": True, "merit": True, "feasibility": True,
                         "acceptance": True, "reason": "Small synthetic action with fixed expected labels."})

    def execute(state, root):
        token = state["inflight"]["token"]
        path = root / (token + ".json")
        # Existing receipt wins; an actual executor needs its own idempotency.
        if path.exists():
            return envelope(json.loads(path.read_text()), 1)
        labels = ["  ALPHA ", "Beta", " gamma"]
        normalized = [s.lower() if state["plan"]["approach"] == "case-only" else s.strip().lower() for s in labels]
        output = root / (token + "-labels.json")
        output.write_text(json.dumps(normalized) + "\n")
        receipt = {"attempt_id": token, "status": "completed", "evidence": [evidence(output, root)]}
        with path.open("x") as handle:
            json.dump(receipt, handle)
        return envelope(receipt, 1)

    def verify(state, root):
        refs = state["result"]["evidence"]
        labels = json.loads((root / refs[0]["path"]).read_text())
        passed = labels == ["alpha", "beta", "gamma"]
        return envelope({"valid": True, "improved": passed, "goal_met": passed,
                         "checks": {"exact_labels": passed}, "evidence": refs})

    def reflect(state, root):
        passed = state["verification"]["goal_met"]
        lesson = None
        if passed:
            lesson = {"statement": "This label task requires trimming as well as case conversion.",
                      "why_reusable": "Prevents repeating case-only variants on the same input contract.",
                      "evidence": state["verification"]["evidence"]}
        return envelope({"observation": "Exact-label check passed." if passed else "Whitespace remains.",
                         "counterevidence": "Three synthetic labels do not establish general text-cleaning quality.",
                         "next_test": "Stop on verified acceptance." if passed else "Revisit whitespace handling.",
                         "decision": "complete" if passed else "pivot", "lesson": lesson})

    return dict(zip(("RESEARCH", "PLAN", "REVIEW", "EXECUTE", "VERIFY", "REFLECT"),
                    (research, plan, review, execute, verify, reflect)))
