"""Bounded POSIX child-process adapter. No shell, scheduler, model, or network API."""
import hashlib
import json
import os
import re
import signal
import subprocess
import time


def run_local(argv, root, attempt_id, timeout_seconds, max_output_bytes=65536):
    """Return an identity-bound saved receipt; reconcile it, never rerun blindly.

    Commands must stay in their process group and approved workspace. This is
    not a security sandbox or a quota for files written by the command itself.
    """
    if os.name != "posix":
        raise RuntimeError("local_process_group_adapter_requires_POSIX")
    if not re.fullmatch(r"[a-f0-9]{32}", attempt_id) or timeout_seconds <= 0 or max_output_bytes < 1:
        raise ValueError("valid_identity_and_positive_bounds_required")
    receipt_path = root / (attempt_id + "-receipt.json")
    marker = root / (attempt_id + "-intent.json")
    command_digest = hashlib.sha256(json.dumps(argv).encode()).hexdigest()
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        if receipt["attempt_id"] != attempt_id or receipt["command_digest"] != command_digest:
            raise ValueError("idempotency_key_reused_for_different_command")
        from .policy import check_evidence
        check_evidence(receipt["evidence"], root)
        return receipt
    # An interrupted intent requires host/process reconciliation, not relaunch.
    with marker.open("x") as handle:
        json.dump({"attempt_id": attempt_id, "command_digest": command_digest}, handle)
    paths = [root / (attempt_id + suffix) for suffix in ("-stdout.txt", "-stderr.txt")]
    start = time.monotonic()
    reason = None
    with paths[0].open("wb") as stdout, paths[1].open("wb") as stderr:
        process = subprocess.Popen(argv, cwd=root, stdout=stdout, stderr=stderr, start_new_session=True)
        identity = {"attempt_id": attempt_id, "pid": process.pid, "process_group": process.pid,
                    "command_digest": command_digest}
        marker.write_text(json.dumps(identity) + "\n")
        while process.poll() is None:
            if time.monotonic() - start >= timeout_seconds:
                reason = "timeout"
            elif sum(path.stat().st_size for path in paths) > max_output_bytes:
                reason = "output_limit"
            if reason:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                break
            time.sleep(0.01)
        process.wait()
        # Kill any remaining children in this group even if the leader exited.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    observed_sizes = [path.stat().st_size for path in paths]
    if sum(observed_sizes) > max_output_bytes and reason is None:
        reason = "output_limit"
    evidence = []
    remaining = max_output_bytes
    for path in paths:
        keep = min(path.stat().st_size, remaining)
        with path.open("r+b") as handle:
            handle.truncate(keep)
        remaining -= keep
        evidence.append({"path": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    receipt = {"attempt_id": attempt_id, "command_digest": command_digest,
               "status": "completed" if process.returncode == 0 and reason is None else "failed",
               "exit_code": process.returncode, "reason": reason, "evidence": evidence,
               "elapsed_seconds": time.monotonic() - start, "observed_log_bytes": observed_sizes,
               "logs_truncated": sum(observed_sizes) > max_output_bytes}
    temporary = root / (attempt_id + "-receipt.tmp")
    with temporary.open("w") as handle:
        json.dump(receipt, handle)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, receipt_path)
    return receipt
