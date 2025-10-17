from fastapi import APIRouter
from typing import List
from app.models.schemas import OptimizationRequest, OptimizationResult, DepartmentAllocation, ScenarioRequest, ScenarioResult
from app.services.forecasting import estimate_department_future_impact
from app.services.optimization import optimize_budget
from app.agent.graph import run_agent, run_scenarios

router = APIRouter()


@router.post("/direct", response_model=OptimizationResult)
async def direct_optimize(req: OptimizationRequest):
    departments = [h.department for h in req.historical_financials]

    # Estimate impact per dollar using a simple forecast-based heuristic
    impact_per_dollar = {}
    for h in req.historical_financials:
        values = [p.value for p in h.series]
        impact = estimate_department_future_impact(values, req.config.forecast_periods)
        # Avoid divide-by-zero: assume 1 unit ~ 1$ scale for this demo
        impact_per_dollar[h.department] = max(impact, 1e-6)

    allocs = optimize_budget(
        departments=departments,
        impact_per_dollar=impact_per_dollar,
        total_budget=req.constraints.total_budget,
        min_per_dept=req.constraints.min_allocation_per_department,
        max_per_dept=req.constraints.max_allocation_per_department,
    )

    allocations = [DepartmentAllocation(department=d, allocation=a, expected_impact=impact_per_dollar[d] * a) for d, a in allocs.items()]
    total_expected_impact = sum(a.expected_impact for a in allocations)

    return OptimizationResult(allocations=allocations, total_expected_impact=float(total_expected_impact), notes="Direct optimization")


@router.post("/agent", response_model=OptimizationResult)
async def agent_optimize(req: OptimizationRequest):
    result = await run_agent(req)
    return result


@router.post("/scenarios", response_model=List[ScenarioResult])
async def scenarios(req: ScenarioRequest):
    results = await run_scenarios(req)
    return results
