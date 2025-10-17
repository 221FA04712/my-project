from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

app = FastAPI(
    title="Agentic Resource Optimizer",
    description="Forecast and optimize allocation of financial, human, and physical resources",
    version="0.1.0",
    default_response_class=ORJSONResponse,
)

# CORS for local dev and simple static frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"message": "Agentic Resource Optimizer API", "docs": "/docs"}


# Routers are imported late to avoid import cycles during app startup
from app.routers.optimize import router as optimize_router  # noqa: E402
from app.routers.data import router as data_router  # noqa: E402

app.include_router(optimize_router, prefix="/optimize", tags=["optimize"])
app.include_router(data_router, prefix="/data", tags=["data"])


