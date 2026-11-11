"""LangGraph routes only unfinished work; SQLite is the execution authority."""
from typing import TypedDict

from .policy import PHASES


class GraphState(TypedDict):
    steps: int
    result: dict


def build_graph(workflow, handlers, max_steps=14):
    from langgraph.graph import END, START, StateGraph

    if not isinstance(max_steps, int) or max_steps < 1:
        raise ValueError("positive_wakeup_step_limit_required")

    def route(state):
        live = workflow.view()
        if state.get("steps", 0) >= max_steps or live["inflight"]:
            return END
        if live["status"] != "ready" or live["mode"] in ("pause", "stop"):
            return END
        if state.get("result", {}).get("status") in ("plan_only", "stale_route"):
            return END
        return live["phase"]

    def node(phase):
        def run(state):
            result = workflow.tick(handlers, expected_phase=phase)
            return {"steps": state.get("steps", 0) + 1, "result": result}
        return run

    graph = StateGraph(GraphState)
    for phase in PHASES:
        graph.add_node(phase, node(phase))
        graph.add_conditional_edges(phase, route, {**{p: p for p in PHASES}, END: END})
    graph.add_conditional_edges(START, route, {**{p: p for p in PHASES}, END: END})
    # Restart the short-lived graph on each wake. Durable module receipts live
    # in SQLite, avoiding a second checkpointer that could replay external work.
    return graph.compile()
