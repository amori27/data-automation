"""Pydantic models for the Data Automation API."""

from pydantic import BaseModel


class PipelineRequest(BaseModel):
    """Request body for the /run endpoint."""

    source: str  # "csv" or "sql"
    source_path: str | None = None
    query: str | None = None
    recipient: str | None = None


class PipelineResponse(BaseModel):
    """Response payload after a pipeline run."""

    report_path: str
    rows: int
