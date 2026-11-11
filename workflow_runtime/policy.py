"""Deterministic checks; these cannot judge scientific merit or semantic novelty."""
import hashlib
import json
import math
from pathlib import Path
import shutil


# RESUME is accepted for old databases; new cycles route inside the transaction.
PHASES = ("RESEARCH", "PLAN", "REVIEW", "EXECUTE", "VERIFY", "REFLECT", "RESUME")


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def fingerprint(plan):
    # Display names and candidate directories do not change experiment identity.
    return digest({key: plan[key] for key in ("approach", "change", "inputs", "evaluation")})


def workspace_bytes(root, max_files):
    size = 0
    for count, path in enumerate(Path(root).rglob("*"), 1):
        if count > max_files:
            raise ValueError("workspace_file_limit")
        if path.is_symlink():
            raise ValueError("workspace_symlink_requires_host_review")
        if path.is_file():
            size += path.stat().st_size
    return size


def check_resources(state, root, launch=False):
    limits = state["contract"]["limits"]
    if state["cycles"] >= limits["max_cycles"]:
        raise ValueError("cycle_limit")
    if state["unknown_cost"]:
        raise ValueError("unknown_cost_requires_reconciliation")
    if state["spent"] >= limits["max_cost"] or state["seconds"] >= limits["max_seconds"]:
        raise ValueError("campaign_limit")
    if shutil.disk_usage(root).free < limits["min_free_bytes"]:
        raise ValueError("insufficient_free_space")
    if not launch:
        return
    used = workspace_bytes(root, limits["max_workspace_files"])
    if used >= limits["max_workspace_bytes"]:
        raise ValueError("workspace_size_limit")
    plan = state["plan"]
    if state["spent"] + plan["estimated_cost"] > limits["max_cost"]:
        raise ValueError("insufficient_campaign_cost")
    if state["seconds"] + plan["estimated_seconds"] > limits["max_seconds"]:
        raise ValueError("insufficient_campaign_time")
    if used + plan["estimated_bytes"] > limits["max_workspace_bytes"]:
        raise ValueError("insufficient_workspace_reserve")


def check_plan(state):
    plan = state["plan"]
    deliberate = state["contract"].get("effort", "deliberate") == "deliberate" or state["research"] is not None
    fields = ("approach", "change", "inputs", "evaluation", "action")
    if deliberate:
        fields += ("hypothesis", "falsifier")
    for key in fields:
        if not isinstance(plan.get(key), str) or not plan[key].strip():
            raise ValueError("missing_plan_" + key)
    for key in ("estimated_cost", "estimated_seconds", "estimated_bytes"):
        if not number(plan.get(key)):
            raise ValueError("invalid_plan_" + key)
    alternatives = (state["research"] or {}).get("alternatives", [])
    if deliberate and (len(set(alternatives)) < 2 or plan["approach"] not in alternatives):
        raise ValueError("compare_two_approaches_before_execution")
    identity = fingerprint(plan)
    attempts = state["attempts"]
    if any(item["fingerprint"] == identity for item in attempts):
        raise ValueError("duplicate_experiment_requires_new_inputs_or_change")
    if sum(item["approach"] == plan["approach"] for item in attempts) >= state["contract"]["limits"]["max_family_attempts"]:
        raise ValueError("approach_attempt_limit")
    if state["plateau"] >= state["contract"]["limits"]["plateau_patience"]:
        recent = attempts[-state["plateau"]:]
        if any(item["approach"] == plan["approach"] for item in recent):
            raise ValueError("plateau_requires_different_approach")
    auth = state["contract"]["authorization"]
    if not auth.get("source") or plan["action"] not in auth.get("allowed_actions", []):
        raise ValueError("action_outside_recorded_scope")


def check_evidence(evidence, root):
    if not isinstance(evidence, list) or not evidence:
        raise ValueError("missing_saved_evidence")
    for item in evidence:
        relative = Path(item["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("evidence_path_outside_workspace")
        path = Path(root) / relative
        if any(parent.is_symlink() for parent in [path, *path.parents]):
            raise ValueError("evidence_symlink")
        if not path.is_file() or path.stat().st_size > 1024 * 1024:
            raise ValueError("evidence_missing_or_exceeds_reference_bound")
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError("evidence_identity_changed")
