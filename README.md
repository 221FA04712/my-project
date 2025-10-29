# Agentic Resource Optimizer

Python + LangGraph agent to forecast and optimize allocation of financial, human, and physical resources.

## Stack
- FastAPI (API)
- LangGraph (agentic workflow)
- scikit-learn (simple forecasting)
- SciPy (linear programming optimization)
- Static frontend (`web/index.html`)

## Setup
```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open the frontend: just open `web/index.html` in your browser.

## Example Request
```json
{
  "historical_financials": [
    { "department": "Education", "series": [ { "period": "2024-Q1", "value": 100 }, { "period": "2024-Q2", "value": 120 }, { "period": "2024-Q3", "value": 140 } ] },
    { "department": "Health",    "series": [ { "period": "2024-Q1", "value": 90 },  { "period": "2024-Q2", "value": 95 },  { "period": "2024-Q3", "value": 110 } ] }
  ],
  "constraints": { "total_budget": 1000 },
  "config": { "objective": "maximize_impact", "forecast_periods": 4 }
}
```

- POST `/optimize/direct` – runs heuristic forecast + LP optimizer
- POST `/optimize/agent` – runs through the LangGraph pipeline

## Notes
- In-memory store (`app/store/memory.py`) is provided for demo; replace with DB for production.
- Add human/physical resource data to `OptimizationRequest` to extend the impact model.
- CORS is wide open for demo; restrict for production.












