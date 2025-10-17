from typing import Any, Dict, List
from app.models.schemas import OptimizationRequest, OptimizationResult, DepartmentAllocation, ScenarioRequest, ScenarioResult, OptimizationConstraints, OptimizationConfig
from app.services.forecasting import estimate_department_future_impact
from app.services.optimization import optimize_budget

# Lazy import to avoid heavy import when not used
try:
    from langgraph.graph import StateGraph, END
except Exception:  # pragma: no cover - allow running without langgraph installed in limited envs
    StateGraph = None  # type: ignore
    END = "END"  # type: ignore


class AgentState(dict):
    pass


def node_prepare(state: AgentState) -> AgentState:
    req: OptimizationRequest = state["request"]
    departments = [h.department for h in req.historical_financials]
    state["departments"] = departments
    return state


def node_forecast(state: AgentState) -> AgentState:
    req: OptimizationRequest = state["request"]
    impact_per_dollar: Dict[str, float] = {}
    for h in req.historical_financials:
        values = [p.value for p in h.series]
        impact = estimate_department_future_impact(values, req.config.forecast_periods)
        impact_per_dollar[h.department] = max(impact, 1e-6)
    state["impact_per_dollar"] = impact_per_dollar
    return state


def node_optimize(state: AgentState) -> AgentState:
    req: OptimizationRequest = state["request"]
    departments: List[str] = state["departments"]
    impact_per_dollar: Dict[str, float] = state["impact_per_dollar"]

    allocs = optimize_budget(
        departments=departments,
        impact_per_dollar=impact_per_dollar,
        total_budget=req.constraints.total_budget,
        min_per_dept=req.constraints.min_allocation_per_department,
        max_per_dept=req.constraints.max_allocation_per_department,
    )
    state["allocations"] = allocs
    return state


def node_report(state: AgentState) -> AgentState:
    impact_per_dollar: Dict[str, float] = state["impact_per_dollar"]
    allocs: Dict[str, float] = state["allocations"]

    allocations = [DepartmentAllocation(department=d, allocation=a, expected_impact=impact_per_dollar[d] * a) for d, a in allocs.items()]
    total_expected_impact = float(sum(a.expected_impact for a in allocations))

    state["result"] = OptimizationResult(
        allocations=allocations,
        total_expected_impact=total_expected_impact,
        notes="Agentic pipeline: prepare -> forecast -> optimize -> report",
    )
    return state


async def run_agent(req: OptimizationRequest) -> OptimizationResult:
    if StateGraph is None:
        # Fallback path if langgraph isn't present; run sequentially
        state: AgentState = {"request": req}
        state = node_prepare(state)
        state = node_forecast(state)
        state = node_optimize(state)
        state = node_report(state)
        return state["result"]

    graph = StateGraph(AgentState)
    graph.add_node("prepare", node_prepare)
    graph.add_node("forecast", node_forecast)
    graph.add_node("optimize", node_optimize)
    graph.add_node("report", node_report)

    graph.set_entry_point("prepare")
    graph.add_edge("prepare", "forecast")
    graph.add_edge("forecast", "optimize")
    graph.add_edge("optimize", "report")
    graph.add_edge("report", END)

    app = graph.compile()
    initial_state: AgentState = {"request": req}
    final_state: AgentState = app.invoke(initial_state)
    return final_state["result"]


async def run_scenarios(scenarios: ScenarioRequest) -> List[ScenarioResult]:
    results: List[ScenarioResult] = []
    base = scenarios.base_request

    for variant in scenarios.variants:
        # Apply overrides to create a per-variant request
        constraints = OptimizationConstraints(
            total_budget=base.constraints.total_budget * variant.budget_multiplier,
            min_allocation_per_department=variant.min_allocation_per_department_override or base.constraints.min_allocation_per_department,
            max_allocation_per_department=variant.max_allocation_per_department_override or base.constraints.max_allocation_per_department,
        )
        config = OptimizationConfig(
            objective=base.config.objective,
            forecast_periods=variant.forecast_periods_override if variant.forecast_periods_override is not None else base.config.forecast_periods,
        )
        req = OptimizationRequest(
            historical_financials=base.historical_financials,
            human_resources=base.human_resources,
            physical_resources=base.physical_resources,
            constraints=constraints,
            config=config,
        )
        res = await run_agent(req)
        results.append(ScenarioResult(name=variant.name, result=res))

    return results
