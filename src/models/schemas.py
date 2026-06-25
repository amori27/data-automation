from pydantic import BaseModel


class PipelineRequest(BaseModel):
    source: str  # "csv" or "sql"
    source_path: str | None = None
    query: str | None = None
    recipient: str | None = None


class PipelineResponse(BaseModel):
    report_path: str
    rows: int
