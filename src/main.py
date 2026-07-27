"""FastAPI application for the Data Automation service.

Exposes endpoints for health checks and triggering the ETL pipeline.
"""

from fastapi import FastAPI
from src.models.schemas import PipelineRequest, PipelineResponse
from src.core.pipeline import run_pipeline

app = FastAPI(title="Data Automation", version="1.0.0")


@app.get("/health")
def health() -> dict:
    """Return service health status."""
    return {"status": "ok"}


@app.post("/run", response_model=PipelineResponse)
def run(req: PipelineRequest) -> PipelineResponse:
    """Execute the ETL pipeline and return the report path.

    Args:
        req: Pipeline configuration (source type, path, optional recipient).
    """
    path = run_pipeline(req.source_path, req.recipient)
    return PipelineResponse(report_path=path, rows=0)
