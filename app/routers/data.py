from typing import Dict, List
from fastapi import APIRouter
from app.models.schemas import DepartmentHistoricalData
from app.store.memory import MemoryStore

router = APIRouter()


@router.post("/ingest")
async def ingest(historical: List[DepartmentHistoricalData]):
    MemoryStore.set("historical_financials", [h.model_dump() for h in historical])
    return {"status": "stored", "departments": [h.department for h in historical]}


@router.get("/historical")
async def get_historical():
    data = MemoryStore.get("historical_financials") or []
    return {"historical_financials": data}












