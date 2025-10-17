from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class TimeSeriesPoint(BaseModel):
    period: str = Field(description="Time period label, e.g., '2024-Q1' or '2025-01'")
    value: float


class DepartmentHistoricalData(BaseModel):
    department: str
    series: List[TimeSeriesPoint]


class HumanResourceData(BaseModel):
    department: str
    headcount: int
    utilization_rate: float = Field(ge=0.0, le=1.0)


class PhysicalResourceData(BaseModel):
    resource: str
    quantity: float
    utilization_rate: float = Field(ge=0.0, le=1.0)


class OptimizationConstraints(BaseModel):
    total_budget: float
    min_allocation_per_department: Optional[Dict[str, float]] = None
    max_allocation_per_department: Optional[Dict[str, float]] = None


class OptimizationConfig(BaseModel):
    objective: str = Field(default="maximize_impact", description="Currently supported: 'maximize_impact'")
    forecast_periods: int = 4


class OptimizationRequest(BaseModel):
    historical_financials: List[DepartmentHistoricalData]
    human_resources: Optional[List[HumanResourceData]] = None
    physical_resources: Optional[List[PhysicalResourceData]] = None
    constraints: OptimizationConstraints
    config: OptimizationConfig = OptimizationConfig()


class DepartmentAllocation(BaseModel):
    department: str
    allocation: float
    expected_impact: float


class OptimizationResult(BaseModel):
    allocations: List[DepartmentAllocation]
    total_expected_impact: float
    notes: Optional[str] = None


# Scenario planning models
class ScenarioVariant(BaseModel):
    name: str
    budget_multiplier: float = 1.0
    forecast_periods_override: Optional[int] = None
    min_allocation_per_department_override: Optional[Dict[str, float]] = None
    max_allocation_per_department_override: Optional[Dict[str, float]] = None


class ScenarioRequest(BaseModel):
    base_request: OptimizationRequest
    variants: List[ScenarioVariant]


class ScenarioResult(BaseModel):
    name: str
    result: OptimizationResult
